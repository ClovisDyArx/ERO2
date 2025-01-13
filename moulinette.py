import simpy
import random
import matplotlib.pyplot as plt
from queue_metrics import QueueMetrics

class Utilisateur:
    """
    Initialise un utilisateur de notre file d'attente

    :param name: Nom de l'étudiant
    :param student_id: Numéro étudiant
    :param promo: Promotion de l'étudiant
    :param workshop: Atelier auquel l'étudiant participe
    """

    def __init__(
        self,
        name: str = "Anonymous",
        student_id: int = None,
        promo: str = "ING",
    ):
        self.name = name
        self.student_id = student_id
        if student_id is None:
            self.student_id = random.randint(1000, 10000)
        self.promo = promo
        self.intelligence = max(min(random.gauss(mu=0.6, sigma=0.075), 0.75), 0.2)
        self.current_exo = 0

    def __str__(self):
        name = self.name
        student_id = self.student_id
        promo = self.promo
        current_exo = self.current_exo
        return f"[{name} ({student_id}) - {promo} | exo {current_exo}]"


class Moulinette:
    """
    Initialise une instance de moulinette.

    :param capacity: Nombre d'utilisateur en simultanée dans la file.
    :param process_time: Temps de process d'un utilisateur dans la file.
    :param tag_limit: Nombre de tag limite par heure (60 unités de temps)
    """

    def __init__(
        self,
        capacity: int = 1,
        process_time: int = 1,
        tag_limit: int = 3,
        nb_exos: int = 5,
    ):
        self.env = simpy.Environment()
        self.server = simpy.Resource(self.env, capacity=capacity)
        self.result_server = simpy.Resource(self.env, capacity=1)
        self.tag_limit = tag_limit
        self.process_time = process_time
        self.nb_exos = nb_exos
        self.users = {}  # user -> [timestep, ...] (maxlen tag_limit)
        self.metrics = QueueMetrics()

    def collect_metrics(self):
        """Collect metrics at regular intervals"""
        while True:
            # Test queue metrics
            test_queue_length = len(self.server.queue)
            test_server_count = self.server.count
            test_utilization = self.server.count / self.server.capacity if self.server.capacity > 0 else 0

            # Result queue metrics
            result_queue_length = len(self.result_server.queue)
            result_server_count = self.result_server.count
            result_utilization = self.result_server.count / self.result_server.capacity if self.result_server.capacity > 0 else 0

            self.metrics.record_state(
                self.env.now,
                test_agents=test_server_count,
                test_queue_length=test_queue_length,
                result_agents=result_server_count,
                result_queue_length=result_queue_length,
                test_server_utilization=test_utilization,
                result_server_utilization=result_utilization
            )

            yield self.env.timeout(1)

    """
    Ajoute un nouvel utilisateur dans la moulinette.

    :param user: Utilisateur.
    """

    def add_user(self, user: Utilisateur = None):
        if user is None:
            user = Utilisateur()
        self.users[user] = []

    """
    Simule l'exécution d'un test pour un utilisateur.

    :param user: Utilisateur.
    """

    def run_test(self, user: Utilisateur):
        user_id = f"{user.name}_{self.env.now}"
        self.metrics.record_test_queue_entry(user_id, self.env.now)

        print(f"{user} enters the queue at {self.env.now}")
        with self.server.request() as request:
            yield request
            print(f"{user} starts testing at {self.env.now}")
            yield self.env.timeout(self.process_time)
            print(f"{user} finishes testing at {self.env.now}")

        self.metrics.record_departure(user_id, self.env.now)

    """
    Lance une simulation complète sur tous les utilisateurs dans la moulinette.

    :param until: Limite de temps de la simulation.
    """

    def start_simulation(self, until: int = 20):
        self.env.process(self.collect_metrics())

        for user in self.users.keys():
            self.env.process(self.run_test(user))

        self.env.run(until=until)

        metrics = self.metrics.calculate_metrics()
        print("\nSimulation Metrics:")
        print("\nTest Queue Metrics:")
        for metric, value in metrics['test_queue'].items():
            print(f"- {metric}: {value}")

        print("\nResult Queue Metrics:")
        for metric, value in metrics['result_queue'].items():
            print(f"- {metric}: {value}")

        print("\nSojourn Times:")
        for queue, times in metrics['sojourn_times'].items():
            print(f"- {queue}:")
            print(f"  - Average: {times['avg']}")
            print(f"  - Variance: {times['var']}")

        print(f"\nThroughput: {metrics['throughput']}")

        # Generate plots
        self.metrics.plot_metrics()
