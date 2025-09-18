def escape_md(text: str) -> str:
    if text is None:
        return ""
    for ch in r"\_*[]()~`>#+-=|{}.!":
        text = text.replace(ch, f"\\{ch}")
    return text

def driver_brief(info: dict) -> str:
    name = escape_md(info.get("name",""))
    parts = [f"👤 Выбран водитель: *{name}*"]
    if info.get("status"): parts.append(f"📊 Статус: {escape_md(info['status'])}")
    if info.get("number"): parts.append(f"📞 Номер: {escape_md(info['number'])}")
    if info.get("about_driver"):
        about = info["about_driver"]
        parts.append(f"ℹ️ О водителе: {escape_md(about[:100] + ('...' if len(about)>100 else ''))}")
    if info.get("date"): parts.append(f"📅 Дата: {escape_md(info['date'])}")
    if "trailer" in info: parts.append("🚛 Прицеп: Да" if info["trailer"] else "🚛 Прицеп: Нет")
    if info.get("notes"):
        notes = info["notes"]
        preview = notes[:200] + ("..." if len(notes) > 200 else "")
        parts.append("\n📝 Текущие заметки:")
        parts.append(escape_md(preview))
    parts.append("\n🎙️ Теперь отправьте запись звонка (аудио) или текстовый комментарий:")
    return "\n".join(parts)

def driver_full(info: dict, comments: list[dict] | None) -> str:
    name = escape_md(info.get("name",""))
    txt = [f"👤 *{name}*\n", f"🆔 `{escape_md(info.get('id',''))[:8]}...`"]
    if info.get("status"): txt.append(f"📊 Статус: {escape_md(info['status'])}")
    if info.get("about_driver"): txt.append(f"ℹ️ О водителе: {escape_md(info['about_driver'])}")
    if info.get("number"): txt.append(f"📞 Номер: {escape_md(info['number'])}")
    if info.get("date"): txt.append(f"📅 Дата: {escape_md(info['date'])}")
    txt.append(f"🚛 Прицеп: {'Да' if info.get('trailer') else 'Нет'}")
    if info.get("notes"):
        txt.append("\n📝 *Заметки:*")
        txt.append(escape_md(info["notes"]))
    if comments:
        txt.append(f"\n💬 *Комментарии ({len(comments)}):*")
        for c in comments[-3:]:
            created = c.get("created_time","")[:16].replace("T"," ")
            body = c.get("text","")
            body = body[:100] + ("..." if len(body) > 100 else "")
            txt.append(f"• [{created or 'Неизвестно'}] {escape_md(body)}")
        if len(comments) > 3:
            txt.append(f"... и еще {len(comments)-3} комментариев")
    else:
        txt.append("\n💬 Комментарии отсутствуют")
    return "\n".join(txt)
