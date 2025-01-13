import random

from moulinette import Moulinette, Utilisateur
from waterfall.infinite import WaterfallMoulinetteInfinite
from waterfall.finite import WaterfallMoulinetteFinite
from waterfall.backup import WaterfallMoulinetteFiniteBackup
from channels_dams.channelsdams import ChannelsAndDams


def create_user_list(names: list[str]) -> list[Utilisateur]:
    """
    Crée une liste d'utilisateurs à partir d'une liste de noms.
    :param names: Liste de noms.
    """
    users = []
    for name in names:
        if random.randint(0, 1) == 0:
            user = Utilisateur(name, promo="ING")
        else:
            user = Utilisateur(name, promo="PREPA")
        users.append(user)
    return users


def moulinette_loadtest(
    moulinette: (
        Moulinette
        | WaterfallMoulinetteInfinite
        | WaterfallMoulinetteFinite
        | WaterfallMoulinetteFiniteBackup
        | ChannelsAndDams
    ),
    user_list: list[Utilisateur],
    until: int = 20,
):
    """
    Charge test la moulinette avec une liste d'utilisateurs.
    :param moulinette: type de moulinette.
    :param user_list: liste d'utilisateurs.
    :param until: nombre de secondes de la simulation.
    """
    for user in user_list:
        moulinette.add_user(user)

    if isinstance(moulinette, ChannelsAndDams):  # /!\ ne pas retirer.
        moulinette.env.process(moulinette.regulate_ing())

    moulinette.start_simulation(until=until)


if __name__ == "__main__":
    user_list = ["Clovis", "Mael", "Florian", "Alexandre", "Pikachu"]
    for _ in range(6):
        user_list.extend(user_list)
    user_list = create_user_list(user_list)

    # print("=== Moulinette (Baseline) ===\n")
    # moulinette = Moulinette(capacity=2, process_time=2)
    # moulinette_loadtest(moulinette, user_list, until=20)

    print("\n\n=== Waterfall Moulinette (Infinite Queues) ===\n")
    wm_inf = WaterfallMoulinetteInfinite(test_capacity=2, test_time=2, result_time=2)
    moulinette_loadtest(wm_inf, user_list, until=5000)

    # print("\n\n=== Waterfall Moulinette (Finite Queues) ===\n")
    # wm_fin = WaterfallMoulinetteFinite(test_capacity=1, ks=2, kf=2, test_time=1, result_time=1)
    # moulinette_loadtest(wm_fin, user_list, until=20)

    # print("\n\n=== Waterfall Moulinette (Finite Queues with Backup) ===\n")
    # wm_fin_back = WaterfallMoulinetteFiniteBackup(test_capacity=1, ks=2, kf=2, test_time=1, result_time=1)
    # moulinette_loadtest(wm_fin_back, user_list, until=20)

    # print("\n\n=== Channels & Dams Moulinette ===\n")
    # cd = ChannelsAndDams(capacity=2, process_time=2, tb=5)
    # moulinette_loadtest(cd, user_list, until=20)
