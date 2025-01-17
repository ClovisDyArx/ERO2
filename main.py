import random

from basics import Utilisateur
from waterfall.infinite import WaterfallMoulinetteInfinite
from waterfall.finite import WaterfallMoulinetteFinite
from waterfall.backup import WaterfallMoulinetteFiniteBackup
from channels_dams.channelsdams import ChannelsAndDams
from typing import List, Callable


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
    until: int | None = None,
    save_filename: str = "metrics.png",
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
    if isinstance(moulinette, WaterfallMoulinetteFiniteBackup) or isinstance(
        moulinette, ChannelsAndDams
    ):
        moulinette.env.process(moulinette.free_backup())

    moulinette.start_simulation(until=until, save_filename=save_filename)


def exec_simulations(nb_user: int, module: Callable, configs: dict):
    for key in configs.keys():
        user_list = create_user_list(generate_users_names(nb_user))
        m_config = module(**configs[key])
        launch_test(
            m_config,
            user_list,
            until=None,
            save_filename=f"output/{m_config.__class__.__name__}_U{len(user_list)}_{key}.png",
        )


if __name__ == "__main__":
    user_lists = {
        "normal": 65,
        "high_load": 130,
        "extreme_load": 300,
    }

    config_infinite = {

    }

    print("\n\n=== Waterfall Moulinette (Infinite Queues) ===\n")
    for load_type, users in user_lists.items():
        print(f"===== {load_type} config =====")
        exec_simulations(users, WaterfallMoulinetteInfinite, config_infinite)

    config_finite = {

    }

    print("\n\n=== Waterfall Moulinette (Finite Queues) ===\n")
    for load_type, users in user_lists.items():
        print(f"===== {load_type} config =====")
        exec_simulations(users, WaterfallMoulinetteFinite, config_finite)

    config_finite_backup = {

    }
    print("\n\n=== Waterfall Moulinette (Finite Queues with Backup) ===\n")
    for load_type, users in user_lists.items():
        print(f"===== {load_type} config =====")
        exec_simulations(users, WaterfallMoulinetteFiniteBackup, config_finite_backup)

    config_channels_dams = {
        "balanced": {  # Balanced configuration with moderate settings
            "K": 3,
            "process_time": 2,
            "result_time": 2,
            "ks": 15,
            "kf": 15,
            "tb": 20,
            "block_option": True
        },
    }
    print("\n\n=== Channels & Dams Moulinette ===\n")
    for load_type, users in user_lists.items():
        print(f"===== {load_type} config =====")
        exec_simulations(users, ChannelsAndDams, config_channels_dams)
