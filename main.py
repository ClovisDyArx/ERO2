import random
import sys
import os

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


def exec_simulations(
    nb_user: int, module: Callable, configs: dict, promo_ratio: float = 0.7
):
    for key in configs.keys():
        user_list = create_user_list(generate_users_names(nb_user), promo_ratio)
        m_config = module(**configs[key])
        if not os.path.exists(os.path.join("output", m_config.__class__.__name__)):
            os.mkdir(os.path.join("output", m_config.__class__.__name__))
            os.mkdir(os.path.join("output", m_config.__class__.__name__, "files"))
            os.mkdir(os.path.join("output", m_config.__class__.__name__, "graphs"))

        with open(
            f"output/{m_config.__class__.__name__}/files/U{len(user_list)}_{key}.txt",
            "w",
        ) as sys.stdout:
            launch_test(
                m_config,
                user_list,
                until=None,
                save_filename=f"output/{m_config.__class__.__name__}/graphs/U{len(user_list)}_{key}.png",
            )
        sys.stdout = sys.__stdout__


if __name__ == "__main__":
    user_lists = {
        "normal": 65,
        "high_load": 130,
        "extreme_load": 300,
    }

    config_infinite = {
        "base": {
            "K": 3,
            "process_time": 2,
            "result_time": 1,
            "tag_limit": 5,
            "nb_exos": 10,
        },
        "high_capacity": {
            "K": 6,
            "process_time": 2,
            "result_time": 1,
            "tag_limit": 5,
            "nb_exos": 10,
        },
        "optimized": {
            "K": 4,
            "process_time": 1,
            "result_time": 1,
            "tag_limit": 7,
            "nb_exos": 10,
        },
        "low_capacity": {
            "K": 1,
            "process_time": 2,
            "result_time": 1,
            "tag_limit": 5,
            "nb_exos": 10,
        },
    }

    print("\n\n=== Waterfall Moulinette (Infinite Queues) ===\n")
    for load_type, users in user_lists.items():
        print(f"===== {load_type} config =====")
        exec_simulations(users, WaterfallMoulinetteInfinite, config_infinite)

    config_finite = {
        "small_queues": {
            "K": 4,
            "process_time": 2,
            "result_time": 1,
            "tag_limit": 5,
            "nb_exos": 10,
            "ks": 20,
            "kf": 5,
        },
        "small_queues_equal": {
            "K": 4,
            "process_time": 2,
            "result_time": 1,
            "tag_limit": 5,
            "nb_exos": 10,
            "ks": 10,
            "kf": 10,
        },
        "medium_queues": {
            "K": 4,
            "process_time": 2,
            "result_time": 1,
            "tag_limit": 5,
            "nb_exos": 10,
            "ks": 20,
            "kf": 10,
        },
        "large_queues": {
            "K": 4,
            "process_time": 2,
            "result_time": 1,
            "tag_limit": 5,
            "nb_exos": 10,
            "ks": 40,
            "kf": 20,
        },
        "large_queue_high_capacity": {
            "K": 6,
            "process_time": 2,
            "result_time": 1,
            "tag_limit": 5,
            "nb_exos": 10,
            "ks": 40,
            "kf": 20,
        },
    }

    print("\n\n=== Waterfall Moulinette (Finite Queues) ===\n")
    for load_type, users in user_lists.items():
        print(f"===== {load_type} config =====")
        exec_simulations(users, WaterfallMoulinetteFinite, config_finite)

    config_finite_backup = {
        "conservative": {
            "K": 3,
            "process_time": 2,
            "result_time": 1,
            "tag_limit": 5,
            "nb_exos": 10,
            "ks": 15,
            "kf": 8,
        },
        "conservative_equal": {
            "K": 3,
            "process_time": 2,
            "result_time": 1,
            "tag_limit": 5,
            "nb_exos": 10,
            "ks": 15,
            "kf": 15,
        },
        "balanced": {
            "K": 4,
            "process_time": 2,
            "result_time": 1,
            "tag_limit": 5,
            "nb_exos": 10,
            "ks": 25,
            "kf": 12,
        },
        "aggressive": {
            "K": 5,
            "process_time": 1,
            "result_time": 1,
            "tag_limit": 6,
            "nb_exos": 10,
            "ks": 35,
            "kf": 15,
        },
    }
    print("\n\n=== Waterfall Moulinette (Finite Queues with Backup) ===\n")
    for load_type, users in user_lists.items():
        print(f"===== {load_type} config =====")
        exec_simulations(users, WaterfallMoulinetteFiniteBackup, config_finite_backup)

    config_channels_dams = {
        "no_regulation_balanced": {
            "K": 3,
            "process_time": 2,
            "result_time": 1,
            "ks": 15,
            "kf": 8,
            "tb": 10,
            "block_option": False,
        },
        "strict_regulation_balanced": {
            "K": 3,
            "process_time": 2,
            "result_time": 1,
            "ks": 15,
            "kf": 8,
            "tb": 10,
            "block_option": True,
        },
        "no_regulation_fast": {
            "K": 5,
            "process_time": 2,
            "result_time": 1,
            "ks": 25,
            "kf": 12,
            "tb": 6,
            "block_option": False,
        },
        "soft_regulation_fast": {
            "K": 5,
            "process_time": 2,
            "result_time": 1,
            "ks": 25,
            "kf": 12,
            "tb": 6,
            "block_option": True,
        },
    }
    print("\n\n=== Channels & Dams Moulinette ===\n")
    for load_type, users in user_lists.items():
        print(f"===== {load_type} config =====")
        exec_simulations(users, ChannelsAndDams, config_channels_dams)
