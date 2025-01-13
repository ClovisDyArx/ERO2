import random

from basics import Utilisateur
from waterfall.infinite import WaterfallMoulinetteInfinite
from waterfall.finite import WaterfallMoulinetteFinite
from waterfall.backup import WaterfallMoulinetteFiniteBackup
from channels_dams.channelsdams import ChannelsAndDams
from typing import List


def generate_users_names(n: int):
    """
    Génère une liste de nom d'utilisateur.

    :param n: nombre de nom à générer.
    """

    return ["USER" + str(i) for i in range(n)]


def create_user_list(names: List[str], promo_ratio=0.5) -> List[Utilisateur]:
    """
    Génère une liste de Utilisateur à partir de names avec une proportion (basée sur tirage aléatoire) de promo_ratio d'ING, et 1 - promo_ratio de PREPA

    :param names: liste de nom d'utilisateur.
    :param promo_ratio: proportion d'ING dans les utilisateurs
    """

    users = []
    for name in names:
        promo = "ING" if random.random() < promo_ratio else "PREPA"
        users.append(Utilisateur(name=name, promo=promo))
    return users


def launch_test(
    moulinette: (
        WaterfallMoulinetteInfinite
        | WaterfallMoulinetteFinite
        | WaterfallMoulinetteFiniteBackup
        | ChannelsAndDams
    ),
    user_list: list[Utilisateur],
    until: int = 100000,
):
    """
    Charge test la moulinette avec une liste d'utilisateurs.

    :param moulinette: type de moulinette.
    :param user_list: liste d'utilisateurs.
    :param until: nombre de secondes de la simulation.
    """

    for user in user_list:
        moulinette.add_user(user)

    # process de régulation de moulinette pour les ING dans le cas de Channels&Dams
    if isinstance(moulinette, ChannelsAndDams):
        moulinette.env.process(moulinette.regulate_ing())

    # process d'utilisation du backup quand le serveur back est libre dans le cas de Waterfall avec backup
    if isinstance(moulinette, WaterfallMoulinetteFiniteBackup):
        moulinette.env.process(moulinette.free_backup())

    moulinette.start_simulation(until=until)


if __name__ == "__main__":
    user_list = create_user_list(generate_users_names(8))

    # print("\n\n=== Waterfall Moulinette (Infinite Queues) ===\n")
    # wm_inf = WaterfallMoulinetteInfinite(K=2, process_time=2, result_time=2)
    # launch_test(wm_inf, user_list)

    # print("\n\n=== Waterfall Moulinette (Finite Queues) ===\n")
    # wm_fin = WaterfallMoulinetteFinite(K=2, ks=2, kf=2, process_time=1, result_time=1)
    # launch_test(wm_fin, user_list)

    # print("\n\n=== Waterfall Moulinette (Finite Queues with Backup) ===\n")
    # wm_fin_back = WaterfallMoulinetteFiniteBackup(
    #     K=2, ks=3, kf=2, process_time=4, result_time=1
    # )
    # launch_test(wm_fin_back, user_list)

    # print("\n\n=== Channels & Dams Moulinette ===\n")
    # cd = ChannelsAndDams(K=2, process_time=2, result_time=2, tb=5, block_option=True)
    # launch_test(cd, user_list)
