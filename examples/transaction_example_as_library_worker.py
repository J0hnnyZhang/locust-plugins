import gevent
import locust
from locust import runners
from locust.main import create_environment
from locust.env import Environment
from examples import transaction_example
from locust import HttpUser, task, SequentialTaskSet
from locust_plugins.transaction_manager import TransactionManager

class ExampleSequentialTaskSet(SequentialTaskSet):
    def on_start(self):
        TransactionManager().on_locust_init(env, env.runner)
        self.tm = TransactionManager()

    @task
    def home(self):
        self.tm.start_transaction("startup")
        self.client.get("/", name="01 /")

    @task
    def get_config_json(self):
        self.client.get("/config.json", name="02 /config.json")
        self.tm.end_transaction("startup")


class TranactionExample(HttpUser):
    host = "https://www.demoblaze.com"
    tasks = [ExampleSequentialTaskSet]

env = Environment(user_classes=[TranactionExample])
env.create_worker_runner("127.0.0.1", 5557)
locust.events.init.fire(environment=env, runner=env.runner)
env.events.report_to_master.add_listener(TransactionManager._report_to_master)
env.runner.greenlet.join()