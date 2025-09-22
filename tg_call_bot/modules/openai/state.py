from aiogram.fsm.state import State, StatesGroup


class AudioStates(StatesGroup):
    waiting_for_audio_transcribe = State()
    waiting_for_audio_summary = State()