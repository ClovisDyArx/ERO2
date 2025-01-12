import simpy
import random

from moulinette import Moulinette


# Attention: une file infinie ici précise qu'on peut avoir un nombre infini d'utilisateur qui attendent dans la file sans se faire refuser.
class WaterfallMoulinetteInfinite(Moulinette):
    """
    Moulinette Waterfall (infinie), avec 2 stages de processing:

    1. Placer le code dans une file d'attente FIFO infinie pour tester. (K serveurs)
    2. Envoyer le résultat dans une file d'attente FIFO infinie. (1 serveur)
    :param test_capacity: capacité de la file d'attente de test.
    :param test_time: Temps de process d'un utilisateur dans la file de test.
    :param result_time: Temps de process d'un utilisateur dans la file de résultat.
    """

    def __init__(self, test_capacity=1, test_time=1, result_time=1):
        super().__init__(capacity=test_capacity, process_time=test_time)
        self.result_server = simpy.Resource(self.env, capacity=1)
        self.result_time = result_time

    def run_test(self, user):
        """
        Simule l'exécution d'un tag dans la file de test et la réception du résultat.
        """

        # File d'attente de test
        for exo in range(self.nb_exos):
            tmp_intelligence = user.intelligence
            while True:
                if (
                    len(self.users[user]) < self.tag_limit
                    or self.users[user][0] <= self.env.now - 60
                ):
                    if len(self.users[user]) != 0:
                        self.users[user].pop(0)

                    user.current_exo = exo
                    print(f"{user} enters the test queue at {self.env.now} ")
                    with self.server.request() as request:
                        yield request
                        print(f"{user} starts testing at {self.env.now}")
                        yield self.env.timeout(self.process_time)
                        print(f"{user} finishes testing at {self.env.now}")

                    # File d'attente résultats
                    with self.result_server.request() as request:
                        print(f"{user} enters the result queue at {self.env.now}")
                        yield request
                        print(f"{user} starts result processing at {self.env.now}")
                        yield self.env.timeout(self.result_time)
                        print(f"{user} finishes result processing at {self.env.now}")

                    if random.random() <= tmp_intelligence:  # commit est passé
                        print(f"{user} finished exo {exo} ! at {self.env.now}")
                        yield self.env.timeout(random.randint(5, 15))
                        break
                    else:
                        print(
                            f"{user} is granted an IQ refresh ! Exo {exo} failed... at {self.env.now}"
                        )
                        tmp_intelligence = min(
                            1,
                            tmp_intelligence
                            + max(min(random.gauss(mu=0.1, sigma=0.015), 0.2), 0.05),
                        )
                        yield self.env.timeout(random.randint(3, 15))
                        self.users[user].append(self.env.now)

            self.users[user] = []

        self.users[user] = -1
