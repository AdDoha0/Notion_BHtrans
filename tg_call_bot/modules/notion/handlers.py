import logging, os
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from modules.notion.client import get_driver_list, add_comment, get_driver_info, get_driver_comments
from .states import NotionStates
from .keyboards import drivers_kb, cancel_comment_kb, info_list_kb, info_nav_kb, comments_nav_kb
from .formatters import escape_md, driver_brief, driver_full
from .usecases import transcribe_file

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("drivers"))
async def show_drivers_command(message: Message, state: FSMContext):
    await message.answer("🔄 Загружаю список водителей...")
    try:
        drivers = await get_driver_list()
        if not drivers:
            return await message.answer("❌ Водители не найдены в базе данных")
        await message.answer(
            f"👥 Найдено {len(drivers)} водителей.\nВыберите водителя для добавления комментария:",
            reply_markup=drivers_kb(drivers)
        )
        await state.set_state(NotionStates.waiting_for_driver_selection)
    except Exception as e:
        logger.exception("Ошибка при получении списка водителей")
        await message.answer("❌ Произошла ошибка при загрузке списка водителей")

@router.callback_query(F.data.startswith("driver_select:"))
async def handle_driver_selection(callback: CallbackQuery, state: FSMContext):
    driver_id = callback.data.split(":", 1)[1]
    try:
        info = await get_driver_info(driver_id)
        if not info:
            return await callback.answer("❌ Не удалось получить информацию о водителе")
        await state.update_data(selected_driver_id=driver_id, selected_driver_name=info.get("name",""))
        await callback.message.edit_text(
            driver_brief(info),
            reply_markup=cancel_comment_kb(),
            parse_mode="Markdown"
        )
        await state.set_state(NotionStates.waiting_for_comment)
        await callback.answer()
    except Exception:
        logger.exception("Ошибка при выборе водителя")
        await callback.answer("❌ Произошла ошибка при выборе водителя")

@router.callback_query(F.data == "driver_cancel")
async def handle_driver_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Выбор водителя отменен")
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "comment_cancel")
async def handle_comment_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Добавление комментария отменено")
    await state.clear()
    await callback.answer()

@router.message(StateFilter(NotionStates.waiting_for_comment))
async def handle_comment_input(message: Message, state: FSMContext):
    data = await state.get_data()
    driver_id = data.get("selected_driver_id")
    driver_name = data.get("selected_driver_name", "")
    if not driver_id:
        await message.answer("❌ Ошибка: не найден выбранный водитель")
        return await state.clear()

    processing = None
    comment_text = ""

    try:
        # TEXT
        if message.text:
            comment_text = message.text.strip()
            if not comment_text:
                return await message.answer("❌ Комментарий не может быть пустым. Попробуйте еще раз:")
            processing = await message.answer("💾 Сохраняю комментарий в Notion...")

        # VOICE
        elif message.voice:
            processing = await message.answer("🎙️ Обрабатываю аудио...")
            from share.promt_utils import get_promt_call_analyze
            system_prompt = get_promt_call_analyze()
            comment_text = await transcribe_file(message.bot, message.voice.file_id, "voice.ogg", system_prompt)
            await processing.edit_text("💾 Сохраняю комментарий в Notion...")

        # AUDIO/DOCUMENT
        elif message.audio or message.document:
            processing = await message.answer("🎙️ Обрабатываю аудиофайл...")
            from share.promt_utils import get_promt_call_analyze
            system_prompt = get_promt_call_analyze()
            if message.audio:
                comment_text = await transcribe_file(message.bot, message.audio.file_id, message.audio.file_name or "audio.mp3", system_prompt)
            else:
                name = message.document.file_name or "audio.mp3"
                comment_text = await transcribe_file(message.bot, message.document.file_id, name, system_prompt)
            await processing.edit_text("💾 Сохраняю комментарий в Notion...")

        else:
            return await message.answer("❌ Отправьте аудиозапись или текстовый комментарий:")

        if not comment_text.strip():
            return await processing.edit_text("❌ Не удалось получить текст для комментария. Попробуйте еще раз:")

        # SAVE to Notion
        ok = await add_comment(driver_id, comment_text)
        if ok:
            show = comment_text[:500] + ("..." if len(comment_text) > 500 else "")
            try:
                await processing.edit_text(
                    f"✅ Комментарий успешно добавлен!\n\n"
                    f"👤 *Водитель:* {escape_md(driver_name)}\n"
                    f"📝 *Комментарий:*\n{escape_md(show)}",
                    parse_mode="Markdown"
                )
            except Exception:
                await processing.edit_text(
                    f"✅ Комментарий успешно добавлен!\n\n"
                    f"👤 Водитель: {driver_name}\n"
                    f"📝 Комментарий:\n{show}"
                )
        else:
            await processing.edit_text("❌ Не удалось добавить комментарий. Попробуйте позже.")

        await state.clear()

    except Exception:
        logger.exception("Ошибка при добавлении комментария")
        if processing:
            await processing.edit_text("❌ Произошла ошибка при добавлении комментария")
        else:
            await message.answer("❌ Произошла ошибка при добавлении комментария")
        await state.clear()

@router.message(Command("driver_info"))
async def show_driver_info_command(message: Message):
    await message.answer("🔄 Загружаю список водителей...")
    try:
        drivers = await get_driver_list()
        if not drivers:
            return await message.answer("❌ Водители не найдены в базе данных")
        await message.answer(
            f"👥 Найдено {len(drivers)} водителей.\nВыберите водителя:",
            reply_markup=info_list_kb(drivers)
        )
    except Exception:
        logger.exception("Ошибка при загрузке списка водителей")
        await message.answer("❌ Произошла ошибка при загрузке списка водителей")

@router.callback_query(F.data.startswith("info_show:"))
async def show_detailed_driver_info(callback: CallbackQuery):
    driver_id = callback.data.split(":", 1)[1]
    try:
        info = await get_driver_info(driver_id)
        if not info:
            return await callback.answer("❌ Не удалось получить информацию о водителе")
        comments = await get_driver_comments(driver_id)
        await callback.message.edit_text(
            driver_full(info, comments),
            reply_markup=info_nav_kb(),
            parse_mode="Markdown"
        )
        await callback.answer()
    except Exception:
        logger.exception("Ошибка при получении информации о водителе")
        await callback.answer("❌ Произошла ошибка при получении информации")

@router.callback_query(F.data == "info_cancel")
async def handle_info_cancel(callback: CallbackQuery):
    await callback.message.edit_text("ℹ️ Просмотр информации завершен")
    await callback.answer()

@router.callback_query(F.data.startswith("show_comments:"))
async def show_all_comments(callback: CallbackQuery):
    driver_id = callback.data.split(":", 1)[1]
    try:
        info = await get_driver_info(driver_id)
        comments = await get_driver_comments(driver_id)
        if not info:
            return await callback.answer("❌ Не удалось получить информацию о водителе")

        lines = [f"💬 *Все комментарии к {escape_md(info.get('name',''))}*\n", f"Всего: {len(comments) if comments else 0}\n"]
        if comments:
            for i, c in enumerate(comments, 1):
                created = c.get("created_time","")[:16].replace("T"," ")
                text = c.get("text","")
                lines.append(f"*{i}.* [{created or 'Неизвестно'}]\n{escape_md(text)}\n")
        else:
            lines.append("Комментарии отсутствуют")

        await callback.message.edit_text(
            "\n".join(lines),
            reply_markup=comments_nav_kb(driver_id),
            parse_mode="Markdown"
        )
        await callback.answer()
    except Exception:
        logger.exception("Ошибка при показе всех комментариев")
        await callback.answer("❌ Произошла ошибка при загрузке комментариев")

@router.callback_query(F.data == "back_to_drivers")
async def back_to_drivers_list(callback: CallbackQuery):
    try:
        drivers = await get_driver_list()
        await callback.message.edit_text(
            f"👥 Найдено {len(drivers)} водителей.\nВыберите водителя:",
            reply_markup=info_list_kb(drivers)
        )
        await callback.answer()
    except Exception:
        logger.exception("Ошибка при возврате к списку")
        await callback.answer("❌ Произошла ошибка при загрузке списка")
