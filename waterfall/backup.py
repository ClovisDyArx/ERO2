import simpy
import random

from .finite import WaterfallMoulinetteFinite
from basics import Commit


class WaterfallMoulinetteFiniteBackup(WaterfallMoulinetteFinite):
    """
    Moulinette Waterfall Finie utilisant FilterStore, avec 2 stages de processing :

    1. Placer le code dans une file d'attente FIFO finie (taille ks) pour exécuter des tests. (K serveurs)
    2. Envoyer le résultat dans une file d'attente FIFO finie (taille kf) pour l'envoyer au front. (1 serveur)

    :param K: Nombre de FIFO pour les tests.
    :param process_time: Temps de process d'un utilisateur dans la file de test.
    :param result_time: Temps de process d'un utilisateur dans la file de résultat.
    :param ks: Tailles des FIFOs pour exécuter des tests.
    :param kf: Taille de la FIFO pour l'envoi des résultats.
    """

    def __init__(
        self,
        K: int = 1,
        process_time: int = 1,
        result_time: int = 1,
        ks: int = 1,
        kf: int = 1,
    ):
        super().__init__(K, ks, kf, process_time, result_time)
        self.backup_storage = simpy.FilterStore(self.env)

    def free_backup(self):
        while True:
            if all(value == -1 for value in self.users_commit_time.values()):
                break

            # si des commits dans le backup et que la queue d'envoi de résultat est libre
            if (
                len(self.backup_storage.items) > 0
                and len(self.result_queue.items) < self.kf
            ):
                commit: Commit = self.backup_storage.get().value
                if commit.exo != self.users_exo[commit.user]:
                    yield self.env.timeout(1)
                    continue

                print(f"{commit} : enters the result queue. [BACKUP]")
                yield self.result_queue.put(commit.user)
                with self.result_server.request() as request:
                    yield request
                    print(f"{commit} : starts result processing. [BACKUP]")
                    yield self.env.timeout(self.result_time)
                    print(f"{commit} : finishes result processing. [BACKUP]")
                    yield self.result_queue.get(lambda x: x == commit.user)

                if random.random() <= commit.chance_to_pass:
                    print(
                        f"{commit} : commit passed for exo {self.users_exo[commit.user]} ! [BACKUP]"
                    )

                    self.users_exo[commit.user] += 1
                    self.users_commit_time[commit.user] = []

            else:
                yield self.env.timeout(1)

    def handle_commit(self, user):
        while self.users_exo[user] < self.nb_exos:
            last_chance_commit = None

            while True:
                # push autorisé si dans la limite de tag
                if (
                    len(self.users_commit_time[user]) < self.tag_limit
                    or self.users_commit_time[user][0] <= self.env.now - 60
                ):
                    commit = Commit(
                        user, self.env.now, self.users_exo[user], last_chance_commit
                    )

                    # si plus de place dans la FIFO de test, refus
                    if len(self.test_queue.items) >= self.ks:
                        print(f"{commit} : refused at test queue (FULL).")
                        self.refusals_test += 1
                        yield self.env.timeout(random.randint(4, 10))
                        continue

                    # pop le commit le plus vieux
                    if len(self.users_commit_time[user]) == self.tag_limit:
                        self.users_commit_time[user].pop(0)

                    # fifo serveur de test
                    print(f"{commit} : enters the test queue.")
                    yield self.test_queue.put(user)
                    with self.server.request() as request:
                        yield request
                        print(f"{commit} : starts testing.")
                        yield self.env.timeout(self.process_time)
                        print(f"{commit} : finishes testing.")
                        yield self.test_queue.get(lambda x: x == user)

                    # si plus de place dans la FIFO d'envoi, refus
                    if len(self.result_queue.items) >= self.kf:
                        print(
                            f"{commit} : refused at result queue (FULL). The result is backed up."
                        )
                        # on ajoute le commit dans le backup
                        self.backup_storage.put(commit)

                        self.refusals_result += 1
                        yield self.env.timeout(random.randint(4, 10))
                        continue

                    # fifo serveur d'envoi
                    print(f"{commit} : enters the result queue.")
                    yield self.result_queue.put(user)
                    with self.result_server.request() as request:
                        yield request
                        print(f"{commit} : starts result processing.")
                        yield self.env.timeout(self.result_time)
                        print(f"{commit} : finishes result processing.")
                        yield self.result_queue.get(lambda x: x == user)

                    # si le commit est bon
                    if random.random() <= commit.chance_to_pass:
                        print(
                            f"{commit} : commit passed for exo {self.users_exo[user]} !"
                        )
                        yield self.env.timeout(random.randint(5, 15))
                        break
                    else:
                        print(
                            f"{commit} : commit failed for exo {self.users_exo[user]}... Increasing chance to pass for next commit."
                        )
                        last_chance_commit = min(
                            1,
                            commit.chance_to_pass
                            + max(min(random.gauss(mu=0.1, sigma=0.015), 0.2), 0.05),
                        )
                        self.users_commit_time[user].append(self.env.now)
                        yield self.env.timeout(random.randint(3, 15))

            self.users_exo[user] += 1
            self.users_commit_time[user] = []

        self.users_commit_time[user] = -1
