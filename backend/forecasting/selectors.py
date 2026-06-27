from forecasting.models import ForecastRun


def forecast_runs_for_business(business):
    return ForecastRun.objects.filter(business=business).prefetch_related('periods')
