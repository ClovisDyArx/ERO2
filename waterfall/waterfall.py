import simpy
import random

from moulinette import Moulinette, Utilisateur


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
                            f"{user} is granted a QI refresh ! Exo {exo} failed... at {self.env.now}"
                        )
                        tmp_intelligence = min(
                            1,
                            tmp_intelligence
                            + max(min(random.gauss(mu=0.1, sigma=0.015), 0.2), 0.05),
                        )
                        yield self.env.timeout(random.randint(3, 15))
                        self.users[user].append(self.env.now)

            self.users[user] = []


class WaterfallMoulinetteFinite(WaterfallMoulinetteInfinite):
    """
    Simule une moulinette Waterfall avec des tailles finies de files, utilisant FilterStore.

    :param test_capacity: capacité de la file d'attente de test.
    :param ks: Tailles des files de test.
    :param kf: Taille de la file de résultat.
    :param test_time: Temps de process d'un utilisateur dans la file de test.
    :param result_time: Temps de process d'un utilisateur dans la file de résultat.
    """

    def __init__(self, test_capacity=1, ks=1, kf=1, test_time=1, result_time=1):
        super().__init__(test_capacity, test_time, result_time)
        self.ks = ks
        self.kf = kf
        self.test_queue = simpy.FilterStore(self.env, capacity=self.ks)
        self.result_queue = simpy.FilterStore(self.env, capacity=self.kf)
        self.refusals_test = 0
        self.refusals_result = 0

    def run_test(self, user):
        # On vérifie s'il y a toujours de la place dans file de test
        if len(self.test_queue.items) >= self.ks:
            print(f"{user} is refused entry to the test queue at {self.env.now}")
            self.refusals_test += 1
            return

        # Si oui alors l'utilisateur est accepté
        print(f"{user} enters the test queue at {self.env.now}")
        yield self.test_queue.put(user)
        with self.server.request() as request:
            yield request
            print(f"{user} starts testing at {self.env.now}")
            yield self.env.timeout(self.process_time)
            print(f"{user} finishes testing at {self.env.now}")
            yield self.test_queue.get(lambda x: x == user)

        # On vérifie s'il y a de la place dans la file de résultats
        if len(self.result_queue.items) >= self.kf:
            print(f"{user} is refused entry to the result queue at {self.env.now}")
            self.refusals_result += 1
            return

        # Si oui alors l'utilisateur est accepté
        print(f"{user} enters the result queue at {self.env.now}")
        yield self.result_queue.put(user)
        with self.result_server.request() as request:
            yield request
            print(f"{user} starts result processing at {self.env.now}")
            yield self.env.timeout(self.result_time)
            print(f"{user} finishes result processing at {self.env.now}")
            yield self.result_queue.get(lambda x: x == user)


class WaterfallMoulinetteFiniteBackup(WaterfallMoulinetteFinite):
    """
    Simule une moulinette Waterfall avec des tailles finies de files et avec un Backup.

    :param test_capacity: capacité de la file d'attente de test.
    :param ks: Tailles des files de test.
    :param kf: Taille de la file de résultat.
    :param test_time: Temps de process d'un utilisateur dans la file de test.
    :param result_time: Temps de process d'un utilisateur dans la file de résultat.
    :param backup_capacity: Capacité du backup des résultats.
    """

    def __init__(
        self,
        test_capacity=1,
        ks=1,
        kf=1,
        test_time=1,
        result_time=1,
        backup_capacity=10,
    ):
        super().__init__(test_capacity, ks, kf, test_time, result_time)
        self.backup_storage = simpy.FilterStore(self.env, capacity=backup_capacity)

    def run_test(self, user):
        if len(self.test_queue.items) >= self.ks:
            print(f"{user} is refused entry to the test queue at {self.env.now}")
            self.refusals_test += 1
            return

        self.test_queue.put(user)
        print(f"{user} enters the test queue at {self.env.now}")
        with self.server.request() as request:
            yield request
            self.test_queue.get()
            print(f"{user} starts testing at {self.env.now}")
            yield self.env.timeout(self.process_time)
            print(f"{user} finishes testing at {self.env.now}")

        # On met dans le back up les résultats de la moulinette
        self.backup_storage.put(user)
        print(f"{user} backs up the result at {self.env.now}")

        if len(self.result_queue.items) >= self.kf:
            print(f"{user} is refused entry to the result queue at {self.env.now}")
            self.refusals_result += 1
            return

        # On récupère depuis le back up les résultats
        if self.backup_storage.items:
            user_from_backup = (
                self.backup_storage.get()
            )  # FIXME: trouver comment pretty print ceci comme un Utilisateur... sûrement un probleme de contexte.
            print(f"{user_from_backup} starts result processing at {self.env.now}")
            yield self.env.timeout(self.result_time)
            print(f"{user_from_backup} finishes result processing at {self.env.now}")
        else:
            print(f"No backup available for {user}.")
