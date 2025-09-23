from aiogram.fsm.state import State, StatesGroup

# Состояния для админ панели
class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_main_prompt = State()
    waiting_for_response_template = State()
    waiting_for_summary_main_prompt = State()
    waiting_for_summary_template = State()