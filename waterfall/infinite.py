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

    def __init__(
        self,
        K: int = 1,
        process_time: int = 1,
        result_time: int = 1,
        tag_limit: int = 5,
        nb_exos: int = 10,
    ):
        super().__init__(
            K=K,
            process_time=process_time,
            result_time=result_time,
            tag_limit=tag_limit,
            nb_exos=nb_exos,
        )

    def handle_commit(self, user: Utilisateur):
        """
        Simule la réception et le traitement d'un commit pour un utilisateur.

        :param user: Utilisateur.
        """

        yield self.env.timeout(random.randint(5, 15))

        while self.users_exo[user.name] < self.nb_exos:
            last_chance_commit = None

            while True:
                if self.users_exo[user.name] >= self.nb_exos:
                    break

                # push autorisé si dans la limite de tag
                if (
                    len(self.users_commit_time[user.name]) < self.tag_limit
                    or self.users_commit_time[user.name][0] <= self.env.now - 60
                ):
                    # pop le commit le plus vieux
                    if len(self.users_commit_time[user.name]) == self.tag_limit:
                        self.users_commit_time[user.name].pop(0)

                    exo = self.users_exo[user.name]
                    commit = Commit(user, self.env.now, exo, last_chance_commit)
                    user_id = f"{user.name}_{self.env.now}_{exo}"

                    # test queue metrics
                    self.metrics.record_test_queue_entry(user_id, self.env.now)

                    # métriques queue test
                    print(f"{commit} : enters the test queue.")
                    with self.test_server.request() as request:
                        yield request
                        print(f"{commit} : starts testing.")
                        yield self.env.timeout(self.process_time)
                        print(f"{commit} : finishes testing.")

                    self.metrics.record_test_queue_exit(user_id, self.env.now)

                    # métriques queue résultat
                    self.metrics.record_result_queue_entry(user_id, self.env.now)

                    # fifo serveur d'envoi
                    print(f"{commit} : enters the result queue.")
                    with self.result_server.request() as request:
                        yield request
                        print(f"{commit} : starts result processing.")
                        yield self.env.timeout(self.result_time)
                        print(f"{commit} : finishes result processing.")

                    self.metrics.record_result_queue_exit(user_id, self.env.now)

                    # si le commit est bon
                    if random.random() <= commit.chance_to_pass:
                        print(f"{commit} : commit passed for exo {exo} !")
                        self.users_exo[user.name] += 1
                        self.users_commit_time[user.name] = []
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
                        self.users_commit_time[user.name].append(self.env.now)
                        yield self.env.timeout(random.randint(3, 15))



