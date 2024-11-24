from moulinette import Moulinette, Utilisateur
from waterfall.waterfall import WaterfallMoulinetteInfinite, WaterfallMoulinetteFinite, WaterfallMoulinetteFiniteBackup


if __name__ == "__main__":
    print("=== Moulinette (Baseline) ===\n")
    moulinette = Moulinette(capacity=2, process_time=2)
    moulinette.add_user(Utilisateur("Clovis"))
    moulinette.add_user(Utilisateur("Mael"))
    moulinette.add_user(Utilisateur("Florian"))
    moulinette.add_user(Utilisateur("Alexandre"))
    moulinette.add_user(Utilisateur("Pikachu"))
    
    moulinette.start_simulation(until=20)
    
    print("\n\n=== Waterfall Moulinette (Infinite Queues) ===\n")
    wm_inf = WaterfallMoulinetteInfinite(test_capacity=2, test_time=2, result_time=2)
    wm_inf.add_user(Utilisateur("Clovis"))
    wm_inf.add_user(Utilisateur("Mael"))
    wm_inf.add_user(Utilisateur("Florian"))
    wm_inf.add_user(Utilisateur("Alexandre"))
    wm_inf.add_user(Utilisateur("Pikachu"))
    
    wm_inf.start_simulation(until=20)
    
    print("\n\n=== Waterfall Moulinette (Finite Queues) ===\n")
    wm_fin = WaterfallMoulinetteFinite(test_capacity=1, ks=2, kf=2, test_time=1, result_time=1)
    wm_fin.add_user(Utilisateur("Clovis"))
    wm_fin.add_user(Utilisateur("Mael"))
    wm_fin.add_user(Utilisateur("Florian"))
    wm_fin.add_user(Utilisateur("Alexandre"))
    wm_fin.add_user(Utilisateur("Pikachu"))
    
    wm_fin.start_simulation(until=20)
    
    print("\n\n=== Waterfall Moulinette (Finite Queues with Backup) ===\n")
    wm_fin_back = WaterfallMoulinetteFiniteBackup(test_capacity=1, ks=2, kf=2, test_time=1, result_time=1)
    wm_fin_back.add_user(Utilisateur("Clovis"))
    wm_fin_back.add_user(Utilisateur("Mael"))
    wm_fin_back.add_user(Utilisateur("Florian"))
    wm_fin_back.add_user(Utilisateur("Alexandre"))
    wm_fin_back.add_user(Utilisateur("Pikachu"))
    
    wm_fin_back.start_simulation(until=20)
