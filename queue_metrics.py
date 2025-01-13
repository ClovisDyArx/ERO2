import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from dataclasses import dataclass, field

@dataclass
class QueueMetrics:
    """Store metrics queue system with two queues"""
    # ===== Time series data =====
    timestamps: List[float] = field(default_factory=list)

    # ===== Test queue metrics =====
    # -> number of users waiting in the test queue at each timestamp
    test_queue_lengths: List[int] = field(default_factory=list)
    # -> percentage of test servers being used at each timestamp (0.0 to 1.0)
    test_server_utilization: List[float] = field(default_factory=list)
    # -> number of users currently being processed by test servers
    test_server_count: List[int] = field(default_factory=list)

    # ===== Result queue metrics =====
    # -> number of users waiting in the result queue at each timestamp
    result_queue_lengths: List[int] = field(default_factory=list)
    # -> percentage of result servers being used at each timestamp (0.0 to 1.0)
    result_server_utilization: List[float] = field(default_factory=list)
    # -> number of users currently being processed by result servers
    result_server_count: List[int] = field(default_factory=list)

    # ===== System-wide metrics =====
    # -> total number of users in the entire system at each timestamp
    system_clients: List[int] = field(default_factory=list)

    # ===== Timing tracking for each queue =====
    # -> used to calculate time spent waiting for testing
    test_queue_entry_times: Dict[str, float] = field(default_factory=dict)
    # -> used with entry times to calculate test queue sojourn time
    test_queue_exit_times: Dict[str, float] = field(default_factory=dict)
    # -> used to calculate time spent waiting for results
    result_queue_entry_times: Dict[str, float] = field(default_factory=dict)
    # -> used with entry times to calculate results queue sojourn time
    result_queue_exit_times: Dict[str, float] = field(default_factory=dict)

    # ===== General =====
    test_queue_blocked: int = 0
    result_queue_blocked: int = 0
    total_requests: int = 0


    def record_state(self, env_time: float, test_agents: int, test_queue_length: int,
                    result_agents: int, result_queue_length: int,
                    test_server_utilization: float, result_server_utilization: float):
        """Record system state at a given time"""
        self.timestamps.append(env_time)

        # test queue
        self.test_server_count.append(test_agents)
        self.test_queue_lengths.append(test_queue_length)
        self.test_server_utilization.append(test_server_utilization)

        # result queue
        self.result_server_count.append(result_agents)
        self.result_queue_lengths.append(result_queue_length)
        self.result_server_utilization.append(result_server_utilization)

        # Total users in the system
        self.system_clients.append(test_agents + result_agents + test_queue_length + result_queue_length)

    # === entry / exit
    def record_test_queue_entry(self, user_id: str, time: float):
        """Record entry to test queue"""
        self.test_queue_entry_times[user_id] = time
        self.total_requests += 1

    def record_test_queue_exit(self, user_id: str, time: float):
        """Record exit from test queue"""
        self.test_queue_exit_times[user_id] = time

    def record_result_queue_entry(self, user_id: str, time: float):
        """Record entry to result queue"""
        self.result_queue_entry_times[user_id] = time

    def record_result_queue_exit(self, user_id: str, time: float):
        """Record exit from result queue"""
        self.result_queue_exit_times[user_id] = time
    # ===

    # === blocking
    def record_test_queue_blocked(self):
        """Record blocked request in test queue"""
        self.test_queue_blocked += 1

    def record_result_queue_blocked(self):
        """Record blocked request in result queue"""
        self.result_queue_blocked += 1
    # ===

    def calculate_metrics(self) -> dict:
        """Calculate all metrics"""
        metrics = {}

        # Test queue metrics
        metrics['test_queue'] = {
            'avg_length': np.mean(self.test_queue_lengths),
            'var_length': np.var(self.test_queue_lengths),
            'max_length': np.max(self.test_queue_lengths),
            'avg_utilization': np.mean(self.test_server_utilization),
            'var_utilization': np.var(self.test_server_utilization),
            'blocking_rate': self.test_queue_blocked / self.total_requests if self.total_requests > 0 else 0
        }

        # Result queue metrics
        metrics['result_queue'] = {
            'avg_length': np.mean(self.result_queue_lengths),
            'var_length': np.var(self.result_queue_lengths),
            'max_length': np.max(self.result_queue_lengths),
            'avg_utilization': np.mean(self.result_server_utilization),
            'var_utilization': np.var(self.result_server_utilization),
            'blocking_rate': self.result_queue_blocked / self.total_requests if self.total_requests > 0 else 0
        }

        # Calculate sojourn times for each queue
        test_sojourn_times = []
        result_sojourn_times = []
        total_sojourn_times = []

        for user_id in self.test_queue_entry_times:
            # test-queue sojourn time
            if user_id in self.test_queue_exit_times:
                test_time = self.test_queue_exit_times[user_id] - self.test_queue_entry_times[user_id]
                test_sojourn_times.append(test_time)

            # result-queue sojourn time
            if user_id in self.result_queue_entry_times and user_id in self.result_queue_exit_times:
                result_time = self.result_queue_exit_times[user_id] - self.result_queue_entry_times[user_id]
                result_sojourn_times.append(result_time)

            # total system sojourn time
            if user_id in self.result_queue_exit_times:
                total_time = self.result_queue_exit_times[user_id] - self.test_queue_entry_times[user_id]
                total_sojourn_times.append(total_time)

        # Add sojourn time metrics
        metrics['sojourn_times'] = {
            'test_queue': {
                'avg': np.mean(test_sojourn_times) if test_sojourn_times else 0,
                'var': np.var(test_sojourn_times) if test_sojourn_times else 0,
                'min': np.min(test_sojourn_times) if test_sojourn_times else 0,
                'max': np.max(test_sojourn_times) if test_sojourn_times else 0
            },
            'result_queue': {
                'avg': np.mean(result_sojourn_times) if result_sojourn_times else 0,
                'var': np.var(result_sojourn_times) if result_sojourn_times else 0,
                'min': np.min(result_sojourn_times) if result_sojourn_times else 0,
                'max': np.max(result_sojourn_times) if result_sojourn_times else 0
            },
            'total': {
                'avg': np.mean(total_sojourn_times) if total_sojourn_times else 0,
                'var': np.var(total_sojourn_times) if total_sojourn_times else 0,
                'min': np.min(total_sojourn_times) if total_sojourn_times else 0,
                'max': np.max(total_sojourn_times) if total_sojourn_times else 0
            }
        }

        # /!\ effective throughput
        if self.timestamps:
            total_time = self.timestamps[-1] - self.timestamps[0]
            completed_requests = len([uid for uid in self.test_queue_entry_times
                                   if uid in self.result_queue_exit_times])
            metrics['throughput'] = completed_requests / total_time if total_time > 0 else 0
        else:
            metrics['throughput'] = 0

        return metrics

    def plot_metrics(self):
        """Generate plots for all metrics"""
        _, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        ax1.plot(self.timestamps, self.test_queue_lengths, label='Test queue')
        ax1.plot(self.timestamps, self.result_queue_lengths, label='Result queue')
        ax1.set_title('Queue lengths over time')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Queue length')
        ax1.legend()

        ax2.plot(self.timestamps, self.test_server_utilization, label='Test servers')
        ax2.plot(self.timestamps, self.result_server_utilization, label='Result server')
        ax2.set_title('Server utilization over time')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Utilization')
        ax2.legend()

        ax3.plot(self.timestamps, self.test_server_count, label='Test servers')
        ax3.plot(self.timestamps, self.result_server_count, label='Result server')
        ax3.set_title('Users being served over time')
        ax3.set_xlabel('Time')
        ax3.set_ylabel('Number of users')
        ax3.legend()

        ax4.plot(self.timestamps, self.system_clients)
        ax4.set_title('Total users in the system over time')
        ax4.set_xlabel('Time')
        ax4.set_ylabel('Number of users')

        plt.tight_layout()
        plt.savefig("metrics.png")