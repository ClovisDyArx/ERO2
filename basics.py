import simpy
import random
import string

from queue_metrics import QueueMetrics


class Utilisateur:
    """
    Initialise un utilisateur de notre file d'attente.

    :param name: Nom de l'étudiant.
    :param promo: Promotion de l'étudiant.
    """

    def __init__(
        self,
        name: str,
        promo: str,
    ):
        self.name = name
        self.promo = promo
        self.intelligence = max(min(random.gauss(mu=0.6, sigma=0.075), 0.75), 0.2)

    def __str__(self):
        return f"[{self.name} - {self.promo}]"


class Commit:
    """
    Initialise un commit avec tag dans la file d'attente.

    :param user: autheur du commit.
    :param date: date (timestep de la simulation) du commit
    :param exo: exercice du commit.
    """

    def __init__(
        self, user: Utilisateur, date: int, exo: int, chance_to_pass: float | None
    ):
        self.user = user
        self.id = self._generate_id()
        self.date = date
        self.exo = exo
        self.chance_to_pass = (
            user.intelligence if chance_to_pass == None else chance_to_pass
        )

    def _generate_id(self):
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=6))

    def __str__(self):
        return f"[{self.id} - exo {self.exo} - time {self.date}] by {self.user}"


class Moulinette:
    """
    Initialise une instance de moulinette.

    :param capacity: Nombre d'utilisateur en simultanée dans la file.
    :param process_time: Temps de process d'un utilisateur dans la file.
    :param tag_limit: Nombre de tag limite par heure (60 unités de temps)
    """

    def __init__(
        self,
        capacity: int = 10,
        process_time: int = 1,
        tag_limit: int = 5,
        nb_exos: int = 10,
    ):
        self.env = simpy.Environment()
        self.server = simpy.Resource(self.env, capacity=capacity)
        self.result_server = simpy.Resource(self.env, capacity=1)
        self.tag_limit = tag_limit
        self.process_time = process_time
        self.nb_exos = nb_exos
        self.users_commit_time = {}  # user -> [timestep, ...] (maxlen tag_limit)
        self.users_exo = {}
        self.metrics = QueueMetrics()

    def collect_metrics(self):
        """
        Collect metrics at regular intervals
        """
        while True:
            # Test queue metrics
            test_queue_length = len(self.server.queue)
            test_server_count = self.server.count
            test_utilization = (
                self.server.count / self.server.capacity
                if self.server.capacity > 0
                else 0
            )

            # Result queue metrics
            result_queue_length = len(self.result_server.queue)
            result_server_count = self.result_server.count
            result_utilization = (
                self.result_server.count / self.result_server.capacity
                if self.result_server.capacity > 0
                else 0
            )

            self.metrics.record_state(
                self.env.now,
                test_agents=test_server_count,
                test_queue_length=test_queue_length,
                result_agents=result_server_count,
                result_queue_length=result_queue_length,
                test_server_utilization=test_utilization,
                result_server_utilization=result_utilization,
            )

            yield self.env.timeout(1)

    def add_user(self, user: Utilisateur = None):
        """
        Ajoute un nouvel utilisateur dans la moulinette.

        :param user: Utilisateur.
        """
        if user is None:
            user = Utilisateur()
        self.users_commit_time[user] = []
        self.users_exo[user] = 0

    def handle_commit(self, user: Utilisateur):
        """
        Simule la réception et le traitement d'un commit pour un utilisateur.

        :param user: Utilisateur.
        """
        commit = Commit(user, self.env.now, 0)

        print(f"{commit} : enters the queue.")
        with self.server.request() as request:
            yield request
            print(f"{commit} : starts testing.")
            yield self.env.timeout(self.process_time)
            print(f"{commit} : finishes testing.")

    def start_simulation(self, until: int):
        """
        Lance une simulation complète sur tous les utilisateurs dans la moulinette et affiche des métriques.

        :param until: Limite de temps de la simulation.
        """
        self.env.process(self.collect_metrics())

        for user in self.users_commit_time.keys():
            self.env.process(self.handle_commit(user))

        self.env.run(until=until)

        metrics = self.metrics.calculate_metrics()
        print("\nSimulation Metrics:")
        print("\nTest Queue Metrics:")
        for metric, value in metrics["test_queue"].items():
            print(f"- {metric}: {value}")

        print("\nResult Queue Metrics:")
        for metric, value in metrics["result_queue"].items():
            print(f"- {metric}: {value}")

        print("\nSojourn Times:")
        for queue, times in metrics["sojourn_times"].items():
            print(f"- {queue}:")
            print(f"  - Average: {times['avg']}")
            print(f"  - Variance: {times['var']}")

        print(f"\nThroughput: {metrics['throughput']}")

        self.metrics.plot_metrics()
