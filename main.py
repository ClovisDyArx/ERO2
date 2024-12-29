from moulinette import Moulinette, Utilisateur
from waterfall.waterfall import WaterfallMoulinetteInfinite, WaterfallMoulinetteFinite, WaterfallMoulinetteFiniteBackup


def create_user_list(names: list[str]) -> list[Utilisateur]:
    """
    Crée une liste d'utilisateurs à partir d'une liste de noms.
    :param names: Liste de noms.
    """
    return [Utilisateur(name) for name in names]


def moulinette_loadtest(
        moulinette: Moulinette | WaterfallMoulinetteInfinite | WaterfallMoulinetteFinite | WaterfallMoulinetteFiniteBackup,
        user_list: list[Utilisateur],
        until: int = 20):
    """
    Charge test la moulinette avec une liste d'utilisateurs.
    :param moulinette: type de moulinette.
    :param user_list: liste d'utilisateurs.
    :param until: nombre de secondes de la simulation.
    """
    for user in user_list:
        moulinette.add_user(user)
    moulinette.start_simulation(until=until)


if __name__ == "__main__":
    user_list = create_user_list(["Clovis", "Mael", "Florian", "Alexandre", "Pikachu"])

    print("=== Moulinette (Baseline) ===\n")
    moulinette = Moulinette(capacity=2, process_time=2)
    moulinette_loadtest(moulinette, user_list, until=20)

    print("\n\n=== Waterfall Moulinette (Infinite Queues) ===\n")
    wm_inf = WaterfallMoulinetteInfinite(test_capacity=2, test_time=2, result_time=2)
    moulinette_loadtest(wm_inf, user_list, until=20)

    print("\n\n=== Waterfall Moulinette (Finite Queues) ===\n")
    wm_fin = WaterfallMoulinetteFinite(test_capacity=1, ks=2, kf=2, test_time=1, result_time=1)
    moulinette_loadtest(wm_fin, user_list, until=20)

    print("\n\n=== Waterfall Moulinette (Finite Queues with Backup) ===\n")
    wm_fin_back = WaterfallMoulinetteFiniteBackup(test_capacity=1, ks=2, kf=2, test_time=1, result_time=1)
    moulinette_loadtest(wm_fin_back, user_list, until=20)
