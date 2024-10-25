from django.apps import AppConfig

# Make configurations for weblog_app with default primary key type and app name
class WeblogAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "weblog_app"
