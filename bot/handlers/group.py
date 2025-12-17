from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.db import create_group as create_group_db, add_parcipant_to_group, get_group_exclusions, get_group_parcipants
from bot.schemas.group import GroupStates
from bot.schemas.parcipant import GroupParcipant
import random

router = Router(name="group")


@router.message(Command("create_group"))
async def set_state_create_group(message: Message, state: FSMContext):
    await state.set_state(GroupStates.waiting_for_group_name)
    await message.answer("Введите название группы")


@router.message(GroupStates.waiting_for_group_name)
async def create_group(message: Message, state: FSMContext):
    group_name = message.text.strip()
    await state.update_data({"group_name": group_name})
    await state.set_state(GroupStates.waiting_for_users_for_group)
    await message.answer("Введите username участников группы через запятую")


@router.message(GroupStates.waiting_for_users_for_group)
async def create_group(message: Message, state: FSMContext):
    users = message.text.strip()
    data = await state.get_data()
    group_name = data["group_name"]
    group_uuid = await create_group_db(group_name, message.from_user.id)

    for user in users.split(","):
        stripted_user = user.strip()
        await add_parcipant_to_group(
            group_uuid,
            None,
            stripted_user if stripted_user[1] != "@" else stripted_user[1:],
        )
    await add_parcipant_to_group(
        group_uuid, message.from_user.id, message.from_user.username
    )

    await message.answer(
        f"Группа {group_name} создана! ID: `{group_uuid}`. Отправьте его своим друзьям для участия",
        parse_mode="Markdown",
    )


@router.message(Command("start_draw"))
async def set_state_start_draw(message: Message, state: FSMContext):
    await state.set_state(GroupStates.waiting_for_group_name_for_draw)
    await message.answer("Введите ID группы")

@router.message(GroupStates.waiting_for_group_name_for_draw)
async def start_draw(message: Message, state: FSMContext):
    group_id_text = message.text.strip()

    participants: list[GroupParcipant] = await get_group_parcipants(group_id_text)
    if len(participants) < 2:
        await message.answer("В группе должно быть минимум два участника.")
        await state.clear()
        return

    random.shuffle(participants)

    exclusions: set[tuple[int, int]] = await get_group_exclusions(group_id_text)

    partners = participants.copy()
    drawn: dict[int, GroupParcipant] = {}

    for giver in participants:
        assigned_partner: GroupParcipant | None = None

        for partner in partners:
            if partner.user_id == giver.user_id:
                continue

            if (giver.user_id, partner.username) in exclusions:
                continue

            assigned_partner = partner
            break

        if assigned_partner is None:
            await message.answer(
                "Не удалось построить корректное распределение с учётом всех исключений. "
                "Попробуй изменить /ослабить ограничения."
            )
            await state.clear()
            return

        drawn[giver.user_id] = assigned_partner
        partners.remove(assigned_partner)

    for giver_id, partner in drawn.items():
        text = (
            f"Ты санта для {partner.username or partner.user_id}.\n"
            f"Вот список желаний твоего подопечного: {partner.wishlist or 'не указан'}"
        )
        await message.answer(text)

    await state.clear()
