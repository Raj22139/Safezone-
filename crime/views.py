from django.shortcuts import render
from .models import Area, CrimeRecord


def landing_page(request):
    """Main landing page — public."""
    total_areas   = Area.objects.filter(is_active=True).count()
    high_risk     = Area.objects.filter(risk_level='high',   is_active=True).count()
    medium_risk   = Area.objects.filter(risk_level='medium', is_active=True).count()
    low_risk      = Area.objects.filter(risk_level='low',    is_active=True).count()
    total_records = CrimeRecord.objects.filter(status='approved').count()

    context = {
        'total_areas':   total_areas,
        'high_risk':     high_risk,
        'medium_risk':   medium_risk,
        'low_risk':      low_risk,
        'total_records': total_records,
    }
    return render(request, 'crime/landing.html', context)


def error_404(request, exception):
    return render(request, 'partials/404.html', status=404)


def error_500(request):
    return render(request, 'partials/500.html', status=500)
