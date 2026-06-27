from forecasting.calculations import clamp_days


def forecast_params_from_request(request):
    return {
        'lookback_days': clamp_days(request.GET.get('lookbackDays'), default=30, minimum=7, maximum=365),
        'horizon_days': clamp_days(request.GET.get('horizonDays'), default=14, minimum=7, maximum=90),
    }
