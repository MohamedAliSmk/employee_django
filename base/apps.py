from django.apps import AppConfig
# from .scheduler import start
from django.db.backends.signals import connection_created

class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

    def ready(self):
        # Import within the method to avoid issues with app registry
        from .scheduler import start

        # Connect to the signal to start the scheduler after the first database connection is made
        connection_created.connect(self.start_scheduler, weak=False)

    def start_scheduler(self, **kwargs):
        from .scheduler import start
        start()
    # def ready(self):
    #     start()