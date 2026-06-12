"""
Management command: python manage.py seed_data
Creates sample Areas with REAL GPS coordinates and CrimeRecords.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from crime.models import Area, CrimeRecord
from datetime import date, timedelta
import random


# ── Real GPS coordinates for all seed areas ──
SAMPLE_AREAS = [
    # Delhi
    {"name": "Vasant Vihar",     "city": "New Delhi",  "state": "Delhi",       "pincode": "110057", "risk_score": 22, "trend": "improving",  "lat": 28.5562, "lng": 77.1575},
    {"name": "Connaught Place",  "city": "New Delhi",  "state": "Delhi",       "pincode": "110001", "risk_score": 62, "trend": "stable",     "lat": 28.6315, "lng": 77.2167},
    {"name": "Paharganj",        "city": "New Delhi",  "state": "Delhi",       "pincode": "110055", "risk_score": 87, "trend": "worsening",  "lat": 28.6448, "lng": 77.2167},
    {"name": "Karol Bagh",       "city": "New Delhi",  "state": "Delhi",       "pincode": "110005", "risk_score": 54, "trend": "stable",     "lat": 28.6514, "lng": 77.1907},
    {"name": "Dwarka Sector 12", "city": "New Delhi",  "state": "Delhi",       "pincode": "110078", "risk_score": 18, "trend": "improving",  "lat": 28.5823, "lng": 77.0516},
    {"name": "Lajpat Nagar",     "city": "New Delhi",  "state": "Delhi",       "pincode": "110024", "risk_score": 48, "trend": "stable",     "lat": 28.5677, "lng": 77.2433},
    {"name": "Saket",            "city": "New Delhi",  "state": "Delhi",       "pincode": "110017", "risk_score": 26, "trend": "improving",  "lat": 28.5245, "lng": 77.2066},
    {"name": "Old Delhi",        "city": "New Delhi",  "state": "Delhi",       "pincode": "110006", "risk_score": 79, "trend": "worsening",  "lat": 28.6562, "lng": 77.2410},
    {"name": "Govindi",          "city": "New Delhi",  "state": "Delhi",       "pincode": "110019", "risk_score": 68, "trend": "worsening",  "lat": 28.6258, "lng": 77.2697},
    {"name": "Defence Colony",   "city": "New Delhi",  "state": "Delhi",       "pincode": "110024", "risk_score": 24, "trend": "improving",  "lat": 28.5705, "lng": 77.2342},
    # Mumbai
    {"name": "Dharavi",          "city": "Mumbai",     "state": "Maharashtra", "pincode": "400017", "risk_score": 74, "trend": "stable",     "lat": 19.0422, "lng": 72.8536},
    {"name": "Bandra West",      "city": "Mumbai",     "state": "Maharashtra", "pincode": "400050", "risk_score": 31, "trend": "improving",  "lat": 19.0596, "lng": 72.8295},
    {"name": "Kurla",            "city": "Mumbai",     "state": "Maharashtra", "pincode": "400070", "risk_score": 63, "trend": "stable",     "lat": 19.0726, "lng": 72.8791},
    # Bangalore
    {"name": "Koramangala",      "city": "Bangalore",  "state": "Karnataka",   "pincode": "560034", "risk_score": 28, "trend": "improving",  "lat": 12.9352, "lng": 77.6245},
    {"name": "Indiranagar",      "city": "Bangalore",  "state": "Karnataka",   "pincode": "560038", "risk_score": 35, "trend": "stable",     "lat": 12.9784, "lng": 77.6408},
]

CRIME_TYPES = ['theft', 'violence', 'traffic', 'fraud', 'burglary', 'assault', 'vandalism']
DESCRIPTIONS = [
    "Pickpocketing incident reported near market area.",
    "Violent altercation reported between two groups.",
    "Vehicle collision at busy intersection.",
    "Online fraud targeting elderly residents.",
    "Residential break-in reported.",
    "Physical assault near public transport.",
    "Property damage reported near bus stand.",
    "Chain snatching reported near metro exit.",
    "Cyber crime targeting mobile users.",
    "Traffic accident involving two-wheeler.",
]


class Command(BaseCommand):
    help = 'Seed database with sample areas (with GPS coordinates) and crime records'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('[SafeZone AI] Seeding database...'))

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@safezone.ai', 'admin123')
            admin.profile.role = 'admin'
            admin.profile.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Superuser created: admin / admin123'))

        # Create sample areas WITH real coordinates
        areas_created = 0
        for a in SAMPLE_AREAS:
            obj, created = Area.objects.get_or_create(
                name=a['name'], city=a['city'],
                defaults={
                    'state':      a['state'],
                    'pincode':    a['pincode'],
                    'risk_score': a['risk_score'],
                    'trend':      a['trend'],
                    'latitude':   a['lat'],
                    'longitude':  a['lng'],
                    'is_active':  True,
                }
            )
            # Update coordinates even if area already exists
            if not created and (not obj.latitude or not obj.longitude):
                obj.latitude  = a['lat']
                obj.longitude = a['lng']
                obj.save()
            if created:
                areas_created += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ {areas_created} areas created with GPS coordinates'))

        # Create crime records
        records_created = 0
        areas = list(Area.objects.all())
        for area in areas:
            num = random.randint(3, 12)
            for _ in range(num):
                CrimeRecord.objects.create(
                    area=area,
                    crime_type=random.choice(CRIME_TYPES),
                    description=random.choice(DESCRIPTIONS),
                    incident_date=date.today() - timedelta(days=random.randint(0, 90)),
                    severity=random.randint(1, 10),
                    status='approved',
                )
                records_created += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ {records_created} crime records created'))
        self.stdout.write(self.style.SUCCESS('\n[SafeZone AI] Database seeded successfully!'))
        self.stdout.write('  Admin login → username: admin | password: admin123')
        self.stdout.write('  URL: http://127.0.0.1:8000/admin-panel/')
