import os

from celery import Celery
from celery.schedules import crontab

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # было myproject

app = Celery('config')  # было myproject

# Загружаем настройки из Django settings с префиксом CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим и регистрируем задачи из всех приложений
app.autodiscover_tasks()

# Настройки для celery-beat (периодические задачи)
app.conf.beat_schedule = {
    'block-inactive-users-daily': {
        'task': 'users.tasks.block_inactive_users',
        'schedule': crontab(hour=0, minute=0),
        'options': {'expires': 3600},
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
