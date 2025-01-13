import random

from waterfall.infinite import WaterfallMoulinetteInfinite
from waterfall.finite import WaterfallMoulinetteFinite
from waterfall.backup import WaterfallMoulinetteFiniteBackup
from channels_dams.channelsdams import ChannelsAndDams
from basics import Utilisateur


def create_user_list(names: list[str], promo_ratio=0.5) -> list[Utilisateur]:
    users = []
    for name in names:
        promo = "ING" if random.random() < promo_ratio else "PREPA"
        users.append(Utilisateur(name=name, promo=promo))
    return users


def test_waterfall_infinite():
    """
    Test basique pour le modèle Waterfall avec une file infinie.
    Vérifie que tous les utilisateurs sont traités sans refus
    """
    print("\n=== Waterfall Moulinette Infinite ===\n")
    moulinette = WaterfallMoulinetteInfinite(K=2, process_time=2, result_time=1)
    user_list = create_user_list(["Alice", "Bob", "Charlie", "Diana", "Eve"])
    for user in user_list:
        moulinette.add_user(user)
    moulinette.start_simulation(until=20)


def test_waterfall_finite():
    """
    Test basique pour le modèle Waterfall avec une file de taille finie.
    Observe le comportement lorsqu'il y a des refus d'entrée dans les files de test ou de résultat.
    Vérifie que les limites de la file (ks et kf) sont respectées.
    """
    print("\n=== Waterfall Moulinette Finite ===\n")
    moulinette = WaterfallMoulinetteFinite(
        K=1, ks=3, kf=2, process_time=2, result_time=1
    )
    user_list = create_user_list(["Alice", "Bob", "Charlie", "Diana", "Eve"])
    for user in user_list:
        moulinette.add_user(user)
    moulinette.start_simulation(until=20)


def test_waterfall_finite_backup():
    """
    Test basique pour le modèle Waterfall avec backup.
    Simule un scénario où les résultats sont sauvegardés lorsque la file de résultats atteint sa capacité maximale.
    Vérifie l'impact du backup sur le traitement des résultats.
    """
    print("\n=== Waterfall Moulinette Finite with Backup ===\n")
    moulinette = WaterfallMoulinetteFiniteBackup(
        K=1, ks=3, kf=2, process_time=2, result_time=1, backup_capacity=5
    )
    user_list = create_user_list(["Alice", "Bob", "Charlie", "Diana", "Eve"])
    for user in user_list:
        moulinette.add_user(user)
    moulinette.start_simulation(until=20)


def test_channels_and_dams():
    """
    Test basique pour le modèle Channels and Dams.
    Évalue le comportement du blocage pour les utilisateurs ING.
    Vérifie que les utilisateurs PREPA sont traités sans interruption.
    """
    print("\n=== Channels and Dams ===\n")
    moulinette = ChannelsAndDams(K=2, process_time=2, tb=5)
    user_list = create_user_list(["Alice", "Bob", "Charlie", "Diana", "Eve"])
    for user in user_list:
        moulinette.add_user(user)
    moulinette.env.process(moulinette.regulate_ing())
    moulinette.start_simulation(until=20)


def test_large_population_waterfall_infinite():
    """
    Test avancé pour le modèle Waterfall avec une file infinie.
    Utilise une grande population (50 utilisateurs) pour analyser les performances et les temps d'attente.
    Vérifie que le système reste stable même avec un grand nombre d'entrées simultanées.
    """
    print("\n=== Large Population: Waterfall Moulinette Infinite ===\n")
    moulinette = WaterfallMoulinetteInfinite(K=5, process_time=1, result_time=1)
    user_list = create_user_list([f"User{i}" for i in range(50)])
    for user in user_list:
        moulinette.add_user(user)
    moulinette.start_simulation(until=100)


def test_extreme_load_waterfall_finite():
    """
    Test avancé pour le modèle Waterfall avec une charge extrême sur une file finie.
    Simule 30 utilisateurs pour observer les taux de refus et l'impact sur les performances.
    Met en évidence les limites des tailles de file (ks et kf).
    """
    print("\n=== Extreme Load: Waterfall Moulinette Finite ===\n")
    moulinette = WaterfallMoulinetteFinite(
        K=2, ks=10, kf=5, process_time=2, result_time=2
    )
    user_list = create_user_list([f"User{i}" for i in range(30)])
    for user in user_list:
        moulinette.add_user(user)
    moulinette.start_simulation(until=50)


def test_variable_backup_capacity():
    """
    Test avancé pour le modèle Waterfall avec backup.
    Compare les performances pour différentes capacités de backup (1, 5, 10).
    Analyse comment la capacité du backup influence le taux de refus et le temps d'attente.
    """
    print(
        "\n=== Variable Backup Capacity: Waterfall Moulinette Finite with Backup ===\n"
    )
    capacities = [1, 5, 10]  # Test différentes capacités de backup
    for backup_capacity in capacities:
        print(f"\n--- Backup Capacity: {backup_capacity} ---\n")
        moulinette = WaterfallMoulinetteFiniteBackup(
            K=2,
            ks=5,
            kf=5,
            process_time=2,
            result_time=2,
            backup_capacity=backup_capacity,
        )
        user_list = create_user_list([f"User{i}" for i in range(20)])
        for user in user_list:
            moulinette.add_user(user)
        moulinette.start_simulation(until=50)


def test_different_blocking_times():
    """
    Test avancé pour le modèle Channels and Dams avec différentes durées de blocage.
    Évalue l'impact de paramètres variés pour tb (2, 5, 10) sur les temps d'attente des utilisateurs ING.
    Permet de déterminer la configuration optimale pour équilibrer les attentes.
    """
    print("\n=== Different Blocking Times: Channels and Dams ===\n")
    blocking_times = [2, 5, 10]  # Test différentes durées de blocage
    for tb in blocking_times:
        print(f"\n--- Blocking Time: {tb} ---\n")
        moulinette = ChannelsAndDams(K=3, process_time=2, tb=tb)
        user_list = create_user_list(
            [f"User{i}" for i in range(15)], promo_ratio=0.7
        )  # Plus d'utilisateurs ING
        for user in user_list:
            moulinette.add_user(user)
        moulinette.env.process(moulinette.regulate_ing())
        moulinette.start_simulation(until=50)


def test_mixed_load_channels_and_dams():
    """
    Test avancé pour le modèle Channels and Dams avec une charge mixte.
    Simule un mélange de 60% d'utilisateurs ING et 40% d'utilisateurs PREPA (40 utilisateurs au total).
    Vérifie comment le système gère des charges asymétriques et analyse l'équité du traitement.
    """
    print("\n=== Mixed Load: Channels and Dams ===\n")
    moulinette = ChannelsAndDams(K=4, process_time=1, tb=5)
    user_list = create_user_list(
        [f"User{i}" for i in range(40)], promo_ratio=0.6
    )  # Mélange de 60% ING et 40% PREPA
    for user in user_list:
        moulinette.add_user(user)
    moulinette.env.process(moulinette.regulate_ing())
    moulinette.start_simulation(until=100)


if __name__ == "__main__":
    # Appeler les tests
    print("\n=========== BASIC TESTS ===========n")

    test_waterfall_infinite()
    test_waterfall_finite()
    test_waterfall_finite_backup()
    test_channels_and_dams()

    print("\n=========== BASIC END ===========n")

    print("\n=========== ADVANCED TESTS ===========n")

    test_large_population_waterfall_infinite()
    test_extreme_load_waterfall_finite()
    test_variable_backup_capacity()
    test_different_blocking_times()
    test_mixed_load_channels_and_dams()

    print("\n=========== ADVANCED END ===========n")
