from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.schemas.parcipant import ParcipantStates
from bot.db import (
    add_parcipant_to_group,
    update_wishlist as update_wishlist_db,
    add_exclusion,
    set_ready,
    update_user_id_by_username_for_parcipant,
    get_group_parcipants as get_group_parcipants_db,
)

router = Router(name="parcipant")


@router.message(Command("join_to_group"))
async def set_state_join_to_group(message: Message, state: FSMContext):
    await state.set_state(ParcipantStates.waiting_for_group_id_for_join)
    await message.answer("Введите ID группы")


@router.message(ParcipantStates.waiting_for_group_id_for_join)
async def join_to_group(message: Message, state: FSMContext):
    group_id_text = message.text.strip()
    await update_user_id_by_username_for_parcipant(
        group_id_text, message.from_user.id, message.from_user.username
    )
    await message.answer(f"Вы присоединились к группе `{group_id_text}`")
    await state.clear()


@router.message(Command("update_wishlist"))
async def set_state_update_wishlist(message: Message, state: FSMContext):
    await state.set_state(ParcipantStates.waiting_for_group_id_update_wishlist)
    await message.answer("Введите ID группы")


@router.message(ParcipantStates.waiting_for_group_id_update_wishlist)
async def set_group_id_for_update_wishlist(message: Message, state: FSMContext):
    group_id_text = message.text.strip()
    await state.update_data({"group_id": group_id_text})
    await message.answer(
        f"Введите ссылки на подарки через запятую или прикрепите ссылку на wishlist для группы `{group_id_text}`"
    )
    await state.set_state(ParcipantStates.waiting_for_wishlist)


@router.message(ParcipantStates.waiting_for_wishlist)
async def update_wishlist(message: Message, state: FSMContext):
    wishlist = message.text.strip()
    data = await state.get_data()
    await update_wishlist_db(data["group_id"], message.from_user.id, wishlist)
    await message.answer(f"Ваш список подарков обновлен!")
    await state.clear()


@router.message(Command("exclude_users"))
async def set_state_exclude_users(message: Message, state: FSMContext):
    await state.set_state(ParcipantStates.waiting_for_group_id_exclude_users)
    await message.answer("Введите ID группы")


@router.message(ParcipantStates.waiting_for_group_id_exclude_users)
async def set_group_id_for_exclude_users(message: Message, state: FSMContext):
    group_id_text = message.text.strip()
    await state.update_data({"group_id": group_id_text})
    await message.answer(
        f"Введите username пользователей указанных через запятую, которых нужно исключить из группы `{group_id_text}`"
    )
    await state.set_state(ParcipantStates.waiting_for_exclude_users)


@router.message(ParcipantStates.waiting_for_exclude_users)
async def exclude_users(message: Message, state: FSMContext):
    users = message.text.strip().split(",")
    data = await state.get_data()
    for i, user in enumerate(users):
        stripted_user = user.strip()
        await add_exclusion(
            data["group_id"],
            message.from_user.id,
            stripted_user if stripted_user[1] != "@" else stripted_user[1:],
        )
    await state.clear()
    await message.answer(
        f"Пользователи {users} исключены из вашей выборки `{data['group_id']}`",
        parse_mode="Markdown",
    )


@router.message(Command("set_ready"))
async def set_state_set_ready(message: Message, state: FSMContext):
    await state.set_state(ParcipantStates.waiting_for_group_id_set_ready)
    await message.answer("Введите ID группы")


@router.message(ParcipantStates.waiting_for_group_id_set_ready)
async def set_group_id_for_set_ready(message: Message, state: FSMContext):
    group_id_text = message.text.strip()
    await set_ready(group_id_text, message.from_user.id)
    await message.answer(
        "Вы готовы. Когда все участники подтвердят готовность вам придёт сообщение с username партнером 😉"
    )


@router.message(Command("get_group_parcipants"))
async def set_state_for_get_group_parcipants(message: Message, state: FSMContext):
    await state.set_state(ParcipantStates.waiting_for_group_name_for_get_parcipants)
    await message.answer("Введите id группы")


@router.message(ParcipantStates.waiting_for_group_name_for_get_parcipants)
async def get_group_parcipants(message: Message, state: FSMContext):
    group_name = message.text.strip()
    res = await get_group_parcipants_db(group_name)
    answer = ""
    for user in res:
        answer += f"""
```
username: {user.username}
ready: {user.ready}\n
```
    """
    await message.answer(answer, parse_mode="Markdown")
    await state.clear()
