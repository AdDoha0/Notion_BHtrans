from aiogram.fsm.state import State, StatesGroup

class NotionStates(StatesGroup):
    waiting_for_driver_selection = State()
    waiting_for_comment = State()
