from django.conf import settings


def app_context(request):
    return {
        "APP_NAME": settings.APP_NAME,
        "CURRENCY_SYMBOL": settings.CURRENCY_SYMBOL,
    }

