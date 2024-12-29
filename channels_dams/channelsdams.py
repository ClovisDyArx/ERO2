import simpy
from moulinette import Moulinette, Utilisateur


class ChannelsAndDams(Moulinette):
    """
    Moulinette Channels & Dams, avec un barrage de régulation pour la population ING.
    """
    def __init__(self, capacity: int = 1, process_time: int = 1, tb: int = 5):
        super().__init__(capacity=capacity, process_time=process_time)
        self.tb = tb
        self.is_blocked = False

    def regulate_ing(self):
        """
        Implémentation du "barrage" de régulation pour la population ING.
        """
        while True:
            # On bloque le serveur pour tb temps
            self.is_blocked = True
            print(f"Moulinette blocked for ING population at {self.env.now}")
            yield self.env.timeout(self.tb)

            # On débloque le serveur pour tb/2 temps
            self.is_blocked = False
            print(f"Moulinette unblocked for ING population at {self.env.now}")
            yield self.env.timeout(self.tb / 2)

    def run_test(self, user: Utilisateur):
        """
        Simule l'exécution d'un test pour un utilisateur.
        """
        while True:
            if user.promo == "ING" and self.is_blocked:
                print(f"{user} blocked from entering queue at {self.env.now}")
                yield self.env.timeout(0.5)
            else:
                print(f"{user} enters the queue at {self.env.now}")
                with self.server.request() as request:
                    yield request
                    print(f"{user} starts testing at {self.env.now}")
                    yield self.env.timeout(self.process_time)
                    print(f"{user} finishes testing at {self.env.now}")
                break
