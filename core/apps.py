from django.apps import AppConfig
import os

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        if os.getenv('JOBGUARD_PRELOAD_MODEL', '').strip().lower() not in {'1', 'true', 'yes', 'on'}:
            return

        from .ai_engine import FraudDetector

        FraudDetector()
