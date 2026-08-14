from django.apps import AppConfig


class HrConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hr"
    label = "hr"
    verbose_name = "Human Resources"

    def ready(self):
        # Ensure models are loaded
        from hr.infrastructure import models  # noqa: F401
