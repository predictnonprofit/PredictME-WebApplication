import os

from celery import Celery

from celery.schedules import crontab

from termcolor import cprint

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'predict_me_project.settings')

app = Celery('predict_me_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    # sender.add_periodic_task(10.0, members_app.tasks.check_subscription_status_for_members, name='add every 10')

    # Calls test('world') every 30 seconds
    # sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    # sender.add_periodic_task(
    #     crontab(hour=7, minute=30, day_of_week=1),
    #     test.s('Happy Mondays!'),
    # )


app.conf.beat_schedule = {
    'run-every-60-seconds': {
        'task': 'members_app.tasks.check_subscription_status_for_members',
        'schedule': 60.0,  # every 60 seconds
    },
}
# app.conf.timezone = 'UTC'

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    cprint(f'Request: {self.request!r}', "cyan")
