import simpy
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
        print(f"{user} enters the test queue at {self.env.now}")
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
