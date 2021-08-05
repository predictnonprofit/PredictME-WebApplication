from django.apps import AppConfig


class UsersConfig(AppConfig):
    # name = 'dash_users'
    name = 'users'

    def ready(self):
        import users.signals
