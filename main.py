from moulinette import Moulinette, Utilisateur


if __name__ == "__main__":
    moulinette = Moulinette(capacity=2)
    for i in range(5):
        user = Utilisateur()
        moulinette.add_user(user)
    moulinette.start_simulation(until=20)
