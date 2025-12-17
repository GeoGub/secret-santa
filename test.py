from bot.schemas.parcipant import GroupParcipant
import random

participants = [
    GroupParcipant(user_id=1, username='Gosha', ready=True, wishlist=''),
    GroupParcipant(user_id=2, username='Sonya', ready=True, wishlist=''),
    GroupParcipant(user_id=3, username='Kate K', ready=True, wishlist=''),
    GroupParcipant(user_id=4, username='Igor', ready=True, wishlist=''),
    GroupParcipant(user_id=5, username='Kate S', ready=True, wishlist=''),
    GroupParcipant(user_id=6, username='Boba', ready=True, wishlist=''),
]
partners = participants.copy()

random.shuffle(participants)

exclusions = [
    (1, 'Sonya'),
    (2, 'Gosha'),
    (3, 'Igor'),
    (4, 'Kate K'),
    (5, 'Boba'),
    (6, 'Kate S'),
]

def build_matching(
    participants: list[GroupParcipant],
    exclusions: set[tuple[int, str]],
):
    """
    Пытается построить распределение giver_id -> receiver_id.
    Возвращает словарь или None, если невозможно.
    max_attempts — на случай больших групп, сначала пробуем рандомом.
    """
    drawn = {}

    if len(participants) < 2:
        return None
    
    parcipants_len = len(participants)
    random.shuffle(participants)

    def backtrack(parcipant, giver):
        drawn_i = 0

        for key, value in drawn.items():
            if value.user_id == parcipant.user_id:
                drawn_i += 1
                continue

            if (parcipant.user_id, value.username) in exclusions:
                drawn_i += 1
                continue

            drawn[key], drawn[giver.user_id] = participants[parcipant_i], drawn[key]
            print("Zamena", participants[parcipant_i], drawn[key])
            return True
        return None

    for giver in participants:
        assigned_partner: GroupParcipant | None = None
        parcipant_i = 0

        while parcipant_i < parcipants_len:
            if participants[parcipant_i].user_id == giver.user_id:
                parcipant_i += 1
                continue

            if (giver.user_id, participants[parcipant_i].username) in exclusions:
                parcipant_i += 1
                continue

            if any(partner.username == participants[parcipant_i].username for partner in drawn.values()):
                parcipant_i += 1
                continue

            assigned_partner = participants[parcipant_i]
            break

        if parcipant_i >= parcipants_len:
            print("PIZDEC 1")
            parcipant_i -= 1

        if not assigned_partner:
            assigned_partner = backtrack(participants[parcipant_i], giver)
            if assigned_partner is None:
                print("PIZDEC 2")
                return None
            continue
        drawn[giver.user_id] = assigned_partner
    return drawn

def main():
    for i in range(100):

        res = build_matching(participants, exclusions)
        if res == None:
            print("PIZDEC")
            break
        for giver_id, partner in res.items():
            if partner.user_id == giver_id:
                print("PLOHO")
                return 
            text = (
                f"{giver_id} санта для {partner.username or partner.user_id}.\n"
                f"Вот список желаний твоего подопечного: {partner.wishlist or 'не указан'}"
            )
            print(text)
        print("============")


main()