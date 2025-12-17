from aiogram.fsm.state import StatesGroup, State
from pydantic import BaseModel


class ParcipantStates(StatesGroup):
    waiting_for_group_id_for_join = State()
    waiting_for_group_id_update_wishlist = State()
    waiting_for_wishlist = State()
    waiting_for_group_id_exclude_users = State()
    waiting_for_exclude_users = State()
    waiting_for_group_id_set_ready = State()
    waiting_for_set_ready = State()
    waiting_for_group_name_for_get_parcipants = State()


class GroupParcipant(BaseModel):
    user_id: int | None = None
    username: str
    ready: bool
    wishlist: str
