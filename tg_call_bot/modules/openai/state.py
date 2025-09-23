from aiogram.fsm.state import State, StatesGroup


class AudioStates(StatesGroup):
    waiting_for_audio_transcribe = State()
    waiting_for_audio_analysis = State()  # для детального анализа звонка
    waiting_for_audio_summary = State()   # для профиля водителя (суммаризация)