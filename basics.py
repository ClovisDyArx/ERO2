import simpy
import random
import string


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
        self.tag_limit = tag_limit
        self.process_time = process_time
        self.nb_exos = nb_exos
        self.users_commit_time = {}  # user -> [timestep, ...] (maxlen tag_limit)
        self.users_exo = {}

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
        print(f"{user} enters the queue at {self.env.now}")
        with self.server.request() as request:
            yield request
            print(f"{user} starts testing at {self.env.now}")
            yield self.env.timeout(self.process_time)
            print(f"{user} finishes testing at {self.env.now}")

    def start_simulation(self, until: int):
        """
        Lance une simulation complète sur tous les utilisateurs dans la moulinette.

        :param until: Limite de temps de la simulation.
        """
        for user in self.users_commit_time.keys():
            self.env.process(self.handle_commit(user))

        # need to add process for metrics

        self.env.run(until=until)
