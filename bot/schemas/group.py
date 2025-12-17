from aiogram.fsm.state import StatesGroup, State


class GroupStates(StatesGroup):
    waiting_for_group_name = State()
    waiting_for_users_for_group = State()
    waiting_for_group_name_for_draw = State()
