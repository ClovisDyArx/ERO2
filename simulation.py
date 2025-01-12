class Simulation:
    def __init__(
        self,
        nb_test_server: int,
        test_server_process_time: int,
        back_server_process_time: int,
        tag_limit: int,
        backup_process_time: int,
        test_server_fifo_size: int = -1,
        back_server_fifo_size: int = -1,
        backup: bool = False,
    ):
        self.nb_test_server = nb_test_server
        self.test_server_process_time = test_server_process_time
        self.back_server_process_time = back_server_process_time
        self.tag_limit = tag_limit
        self.backup_process_time = backup_process_time
        self.test_server_fifo_size = test_server_fifo_size
        self.back_server_fifo_size = back_server_fifo_size
        self.backup = backup

    def init_simulation(self):
        pass

    def run_simulation(self):
        pass

    def get_metrics(self):
        pass
