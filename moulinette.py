import simpy
import random


class Utilisateur:
    """
    Initialise un utilisateur de notre file d'attente
    :param name: Nom de l'étudiant
    :param student_id: Numéro étudiant
    :param promo: Promotion de l'étudiant
    :param workshop: Atelier auquel l'étudiant participe
    """
    def __init__(self, name: str = "Anonymous", student_id: int = None, promo: str = "ING", workshop: str = "C"):
        self.name = name
        self.student_id = student_id
        if student_id is None:
            self.student_id = random.randint(1000, 10000)
        self.promo = promo
        self.workshop = workshop
    
    def __str__(self):
        name = self.name
        student_id = self.student_id
        promo = self.promo
        workshop = self.workshop
        return f"[{name} ({student_id}) - {promo} | {workshop}]"
    
    def __getitem__(self):
        return {
            "name": self.name,
            "student_id": self.student_id,
            "promo": self.promo,
            "workshop": self.workshop
        }
    
    def __setitem__(self, name: str, student_id: int, promo: str, workshop: str):
        self.name = name
        self.student_id = student_id
        self.promo = promo
        self.workshop = workshop


class Moulinette:
    """
    Initialise une instance de moulinette.
    :param capacity: Nombre d'utilisateur en simultanée dans la file.
    :param process_time: Temps de process d'un utilisateur dans la file.
    """
    def __init__(self, capacity: int = 1, process_time: int = 1):
        self.env = simpy.Environment()
        self.server = simpy.Resource(self.env, capacity=capacity)
        self.process_time = process_time
        self.users = []

    """
    Ajoute un nouvel utilisateur dans la moulinette.
    :param user: Utilisateur.
    """
    def add_user(self, user: Utilisateur = None):
        if user is None:
            user = Utilisateur()
        self.users.append(user)

    """
    Simule l'exécution d'un test pour un utilisateur.
    :param user: Utilisateur.
    """
    def run_test(self, user: Utilisateur):
        print(f"{user} enters the queue at {self.env.now}")
        with self.server.request() as request:
            yield request
            print(f"{user} starts testing at {self.env.now}")
            yield self.env.timeout(self.process_time)
            print(f"{user} finishes testing at {self.env.now}")

    """
    Lance une simulation complète sur tous les utilisateurs dans la moulinette.
    :param until: Limite de temps de la simulation.
    """
    def start_simulation(self, until: int = 20):
        for user in self.users:
            self.env.process(self.run_test(user))
        self.env.run(until=until)
