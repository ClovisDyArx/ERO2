import random

from basics import Utilisateur, Commit
from waterfall.backup import WaterfallMoulinetteFiniteBackup


class ChannelsAndDams(WaterfallMoulinetteFiniteBackup):
    """
    Moulinette Channels&Dams, avec 3 stages de processing :

    1. Checker si la régulation de la population ING est en place et blocage de la moulinette si nécessaire.
    2. Placer le code dans une file d'attente FIFO finie (taille ks) pour exécuter des tests. (K serveurs)
    3. Envoyer le résultat dans une file d'attente FIFO finie (taille kf) pour l'envoyer au front. (1 serveur)

    Si un blocage survient au niveau du serveur d'envoi du résultat, le résultat du test est envoyé dans un backup.
    Lorsque la queue des résultats est libre, les commits du backup y sont poussés.

    :param K: Nombre de FIFO pour les tests.
    :param process_time: Temps de process d'un utilisateur dans la file de test.
    :param result_time: Temps de process d'un utilisateur dans la file de résultat.
    :param ks: Tailles des FIFOs pour exécuter des tests.
    :param kf: Taille de la FIFO pour l'envoi des résultats.
    :param tb: Temps de blocage de la moulinette pour les ING.
    :param block_option: Permet d'activer ou non la fonction de blocage des ING.
    """

    def __init__(
        self,
        K: int = 1,
        process_time: int = 1,
        result_time: int = 1,
        ks: int = 1,
        kf: int = 1,
        tb: int = 5,
        block_option: bool = False,
    ):
        super().__init__(
            K=K, process_time=process_time, result_time=result_time, ks=ks, kf=kf
        )
        self.tb = tb
        self.block_option = block_option
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
                    if self.block_option and user.promo == "ING" and self.is_blocked:
                        print(f"{commit} : blocked by ING regulation.")
                        yield self.env.timeout(random.randint(1, 3))
                    else:
                        exo = self.users_exo[user]
                        commit = Commit(user, self.env.now, exo, last_chance_commit)
                        user_id = f"{user.name}_{self.env.now}_{exo}"

                        # si plus de place dans la FIFO de test, refus
                        if len(self.test_queue.items) >= self.ks:
                            self.metrics.record_test_queue_blocked(self.env.now)
                            print(f"{commit} : refused at test queue (FULL).")
                            self.refusals_test += 1
                            yield self.env.timeout(random.randint(4, 10))
                            continue

                        # pop le commit le plus vieux
                        if len(self.users_commit_time[user]) == self.tag_limit:
                            self.users_commit_time[user].pop(0)

                        # test queue metrics
                        self.metrics.record_test_queue_entry(user_id, self.env.now)

                        # fifo serveur de test
                        print(f"{commit} : enters the test queue.")
                        yield self.test_queue.put(user)
                        with self.test_server.request() as request:
                            yield request
                            print(f"{commit} : starts testing.")
                            yield self.env.timeout(self.process_time)
                            print(f"{commit} : finishes testing.")
                            yield self.test_queue.get(lambda x: x == user)

                        self.metrics.record_test_queue_exit(user_id, self.env.now)

                        # si plus de place dans la FIFO d'envoi, refus
                        if len(self.result_queue.items) >= self.kf:
                            self.metrics.record_result_queue_blocked(self.env.now)
                            print(
                                f"{commit} : refused at result queue (FULL). The result is backed up."
                            )
                            # on ajoute le commit dans le backup
                            self.backup_storage.put(commit)

                            self.refusals_result += 1
                            yield self.env.timeout(random.randint(4, 10))
                            continue

                        # métriques queue résultat
                        self.metrics.record_result_queue_entry(user_id, self.env.now)

                        # fifo serveur d'envoi
                        print(f"{commit} : enters the result queue.")
                        yield self.result_queue.put(user)
                        with self.result_server.request() as request:
                            yield request
                            print(f"{commit} : starts result processing.")
                            yield self.env.timeout(self.result_time)
                            print(f"{commit} : finishes result processing.")
                            yield self.result_queue.get(lambda x: x == user)

                        self.metrics.record_result_queue_exit(user_id, self.env.now)

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
                                + max(
                                    min(random.gauss(mu=0.1, sigma=0.015), 0.2), 0.05
                                ),
                            )
                            self.users_commit_time[user].append(self.env.now)
                            yield self.env.timeout(random.randint(3, 15))

            self.users_exo[user] += 1
            self.users_commit_time[user] = []

        self.users_commit_time[user] = -1
