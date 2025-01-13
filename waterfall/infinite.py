import simpy
import random

from basics import Moulinette, Utilisateur, Commit


class WaterfallMoulinetteInfinite(Moulinette):
    """
    Moulinette Waterfall Infinie, avec 2 stages de processing :

    1. Placer le code dans une file d'attente FIFO infinie pour exécuter des tests. (K serveurs)
    2. Envoyer le résultat dans une file d'attente FIFO infinie pour l'envoyer au front. (1 serveur)

    :param K: Nombre de FIFO pour les tests.
    :param process_time: Temps de process d'un utilisateur dans la file de test.
    :param result_time: Temps de process d'un utilisateur dans la file de résultat.
    """

    def __init__(self, K: int = 1, process_time: int = 1, result_time: int = 1):
        super().__init__(capacity=K, process_time=process_time)
        self.result_server = simpy.Resource(self.env, capacity=1)
        self.result_time = result_time

    def handle_commit(self, user: Utilisateur):
        """
        Simule la réception et le traitement d'un commit pour un utilisateur.

        :param user: Utilisateur.
        """

        for exo in range(self.nb_exos):
            last_chance_commit = None

            while True:
                # push autorisé si dans la limite de tag
                if (
                    len(self.users_commit_time[user]) < self.tag_limit
                    or self.users_commit_time[user][0] <= self.env.now - 60
                ):
                    # pop le commit le plus vieux
                    if len(self.users_commit_time[user]) == self.tag_limit:
                        self.users_commit_time[user].pop(0)

                    commit = Commit(user, self.env.now, exo, last_chance_commit)

                    # fifo serveur de test
                    print(f"{commit} : enters the test queue.")
                    with self.server.request() as request:
                        yield request
                        print(f"{commit} : starts testing.")
                        yield self.env.timeout(self.process_time)
                        print(f"{commit} : finishes testing.")

                    # fifo serveur d'envoi
                    print(f"{commit} : enters the result queue.")
                    with self.result_server.request() as request:
                        yield request
                        print(f"{commit} : starts result processing.")
                        yield self.env.timeout(self.result_time)
                        print(f"{commit} : finishes result processing.")

                    # si le commit est bon
                    if random.random() <= commit.chance_to_pass:
                        print(f"{commit} : commit passed for exo {exo} !")
                        yield self.env.timeout(random.randint(5, 15))
                        break
                    else:
                        print(
                            f"{commit} : commit failed for exo {exo}... Increasing chance to pass for next commit."
                        )
                        last_chance_commit = min(
                            1,
                            commit.chance_to_pass
                            + max(min(random.gauss(mu=0.1, sigma=0.015), 0.2), 0.05),
                        )
                        self.users_commit_time[user].append(self.env.now)
                        yield self.env.timeout(random.randint(3, 15))

            self.users_commit_time[user] = []

        self.users_commit_time[user] = -1
