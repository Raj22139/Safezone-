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

    # Central Delhi
    {"name": "Connaught Place", "city": "New Delhi", "state": "Delhi", "pincode": "110001", "risk_score": 62, "trend": "stable", "lat": 28.6315, "lng": 77.2167},
    {"name": "Paharganj", "city": "New Delhi", "state": "Delhi", "pincode": "110055", "risk_score": 87, "trend": "worsening", "lat": 28.6448, "lng": 77.2167},
    {"name": "Karol Bagh", "city": "New Delhi", "state": "Delhi", "pincode": "110005", "risk_score": 54, "trend": "stable", "lat": 28.6514, "lng": 77.1907},
    {"name": "Old Delhi", "city": "New Delhi", "state": "Delhi", "pincode": "110006", "risk_score": 79, "trend": "worsening", "lat": 28.6562, "lng": 77.2410},
    {"name": "Daryaganj", "city": "New Delhi", "state": "Delhi", "pincode": "110002", "risk_score": 65, "trend": "stable", "lat": 28.6415, "lng": 77.2433},

    # South Delhi
    {"name": "Saket", "city": "New Delhi", "state": "Delhi", "pincode": "110017", "risk_score": 26, "trend": "improving", "lat": 28.5245, "lng": 77.2066},
    {"name": "Vasant Vihar", "city": "New Delhi", "state": "Delhi", "pincode": "110057", "risk_score": 22, "trend": "improving", "lat": 28.5562, "lng": 77.1575},
    {"name": "Defence Colony", "city": "New Delhi", "state": "Delhi", "pincode": "110024", "risk_score": 24, "trend": "improving", "lat": 28.5705, "lng": 77.2342},
    {"name": "Lajpat Nagar", "city": "New Delhi", "state": "Delhi", "pincode": "110024", "risk_score": 48, "trend": "stable", "lat": 28.5677, "lng": 77.2433},
    {"name": "Greater Kailash", "city": "New Delhi", "state": "Delhi", "pincode": "110048", "risk_score": 32, "trend": "improving", "lat": 28.5484, "lng": 77.2381},
    {"name": "Hauz Khas", "city": "New Delhi", "state": "Delhi", "pincode": "110016", "risk_score": 38, "trend": "stable", "lat": 28.5494, "lng": 77.2001},
    {"name": "Kalkaji", "city": "New Delhi", "state": "Delhi", "pincode": "110019", "risk_score": 58, "trend": "stable", "lat": 28.5416, "lng": 77.2588},

    # West Delhi
    {"name": "Dwarka Sector 12", "city": "New Delhi", "state": "Delhi", "pincode": "110078", "risk_score": 18, "trend": "improving", "lat": 28.5823, "lng": 77.0516},
    {"name": "Janakpuri", "city": "New Delhi", "state": "Delhi", "pincode": "110058", "risk_score": 35, "trend": "stable", "lat": 28.6219, "lng": 77.0878},
    {"name": "Punjabi Bagh", "city": "New Delhi", "state": "Delhi", "pincode": "110026", "risk_score": 44, "trend": "stable", "lat": 28.6692, "lng": 77.1258},
    {"name": "Rajouri Garden", "city": "New Delhi", "state": "Delhi", "pincode": "110027", "risk_score": 47, "trend": "stable", "lat": 28.6425, "lng": 77.1210},

    # East Delhi
    {"name": "Laxmi Nagar", "city": "New Delhi", "state": "Delhi", "pincode": "110092", "risk_score": 72, "trend": "worsening", "lat": 28.6303, "lng": 77.2773},
    {"name": "Preet Vihar", "city": "New Delhi", "state": "Delhi", "pincode": "110092", "risk_score": 46, "trend": "stable", "lat": 28.6415, "lng": 77.2952},
    {"name": "Mayur Vihar", "city": "New Delhi", "state": "Delhi", "pincode": "110091", "risk_score": 42, "trend": "stable", "lat": 28.6067, "lng": 77.2966},

    # North Delhi
    {"name": "Civil Lines", "city": "New Delhi", "state": "Delhi", "pincode": "110054", "risk_score": 30, "trend": "improving", "lat": 28.6767, "lng": 77.2250},
    {"name": "Model Town", "city": "New Delhi", "state": "Delhi", "pincode": "110009", "risk_score": 39, "trend": "stable", "lat": 28.7051, "lng": 77.1931},
    {"name": "Rohini Sector 18", "city": "New Delhi", "state": "Delhi", "pincode": "110089", "risk_score": 51, "trend": "stable", "lat": 28.7374, "lng": 77.1147},

    # North East Delhi
    {"name": "Seelampur", "city": "New Delhi", "state": "Delhi", "pincode": "110053", "risk_score": 84, "trend": "worsening", "lat": 28.6695, "lng": 77.2667},
    {"name": "Shahdara", "city": "New Delhi", "state": "Delhi", "pincode": "110032", "risk_score": 69, "trend": "stable", "lat": 28.6735, "lng": 77.2899},

    # North West Delhi
    {"name": "Pitampura", "city": "New Delhi", "state": "Delhi", "pincode": "110034", "risk_score": 43, "trend": "stable", "lat": 28.7037, "lng": 77.1310},

    # South West Delhi
    {"name": "Najafgarh", "city": "New Delhi", "state": "Delhi", "pincode": "110043", "risk_score": 76, "trend": "worsening", "lat": 28.6097, "lng": 76.9855},

    # South East Delhi
    {"name": "Govindpuri", "city": "New Delhi", "state": "Delhi", "pincode": "110019", "risk_score": 68, "trend": "worsening", "lat": 28.5355, "lng": 77.2649},

    # Mumbai
    {"name": "Dharavi",          "city": "Mumbai",     "state": "Maharashtra", "pincode": "400017", "risk_score": 74, "trend": "stable",     "lat": 19.0422, "lng": 72.8536},
    {"name": "Bandra West",      "city": "Mumbai",     "state": "Maharashtra", "pincode": "400050", "risk_score": 31, "trend": "improving",  "lat": 19.0596, "lng": 72.8295},
    {"name": "Kurla",            "city": "Mumbai",     "state": "Maharashtra", "pincode": "400070", "risk_score": 63, "trend": "stable",     "lat": 19.0726, "lng": 72.8791},
    # South Mumbai
    {"name": "Colaba", "city": "Mumbai", "state": "Maharashtra", "pincode": "400005", "risk_score": 38, "trend": "stable", "lat": 18.9067, "lng": 72.8147},
    {"name": "Fort", "city": "Mumbai", "state": "Maharashtra", "pincode": "400001", "risk_score": 48, "trend": "stable", "lat": 18.9330, "lng": 72.8354},
    {"name": "Marine Lines", "city": "Mumbai", "state": "Maharashtra", "pincode": "400020", "risk_score": 35, "trend": "improving", "lat": 18.9432, "lng": 72.8231},
    {"name": "Crawford Market", "city": "Mumbai", "state": "Maharashtra", "pincode": "400001", "risk_score": 72, "trend": "worsening", "lat": 18.9467, "lng": 72.8342},

    # Central Mumbai
    {"name": "Dadar", "city": "Mumbai", "state": "Maharashtra", "pincode": "400014", "risk_score": 58, "trend": "stable", "lat": 19.0178, "lng": 72.8478},
    {"name": "Parel", "city": "Mumbai", "state": "Maharashtra", "pincode": "400012", "risk_score": 49, "trend": "stable", "lat": 19.0097, "lng": 72.8425},
    {"name": "Byculla", "city": "Mumbai", "state": "Maharashtra", "pincode": "400027", "risk_score": 65, "trend": "stable", "lat": 18.9766, "lng": 72.8335},
    {"name": "Wadala", "city": "Mumbai", "state": "Maharashtra", "pincode": "400031", "risk_score": 52, "trend": "stable", "lat": 19.0179, "lng": 72.8561},

    # High-risk zones
    {"name": "Dharavi", "city": "Mumbai", "state": "Maharashtra", "pincode": "400017", "risk_score": 85, "trend": "worsening", "lat": 19.0422, "lng": 72.8536},
    {"name": "Kurla", "city": "Mumbai", "state": "Maharashtra", "pincode": "400070", "risk_score": 78, "trend": "worsening", "lat": 19.0726, "lng": 72.8791},
    {"name": "Sion", "city": "Mumbai", "state": "Maharashtra", "pincode": "400022", "risk_score": 64, "trend": "stable", "lat": 19.0434, "lng": 72.8610},
    {"name": "Chembur", "city": "Mumbai", "state": "Maharashtra", "pincode": "400071", "risk_score": 55, "trend": "stable", "lat": 19.0522, "lng": 72.9005},

    # Western suburbs
    {"name": "Bandra West", "city": "Mumbai", "state": "Maharashtra", "pincode": "400050", "risk_score": 31, "trend": "improving", "lat": 19.0596, "lng": 72.8295},
    {"name": "Andheri East", "city": "Mumbai", "state": "Maharashtra", "pincode": "400069", "risk_score": 62, "trend": "stable", "lat": 19.1136, "lng": 72.8697},
    {"name": "Andheri West", "city": "Mumbai", "state": "Maharashtra", "pincode": "400053", "risk_score": 47, "trend": "stable", "lat": 19.1364, "lng": 72.8276},
    {"name": "Jogeshwari", "city": "Mumbai", "state": "Maharashtra", "pincode": "400060", "risk_score": 59, "trend": "stable", "lat": 19.1349, "lng": 72.8483},
    {"name": "Goregaon", "city": "Mumbai", "state": "Maharashtra", "pincode": "400062", "risk_score": 44, "trend": "stable", "lat": 19.1648, "lng": 72.8493},
    {"name": "Malad", "city": "Mumbai", "state": "Maharashtra", "pincode": "400064", "risk_score": 53, "trend": "stable", "lat": 19.1864, "lng": 72.8485},
    {"name": "Borivali", "city": "Mumbai", "state": "Maharashtra", "pincode": "400091", "risk_score": 36, "trend": "improving", "lat": 19.2307, "lng": 72.8567},

    # Eastern suburbs
    {"name": "Powai", "city": "Mumbai", "state": "Maharashtra", "pincode": "400076", "risk_score": 29, "trend": "improving", "lat": 19.1176, "lng": 72.9060},
    {"name": "Ghatkopar", "city": "Mumbai", "state": "Maharashtra", "pincode": "400086", "risk_score": 57, "trend": "stable", "lat": 19.0856, "lng": 72.9080},
    {"name": "Vikhroli", "city": "Mumbai", "state": "Maharashtra", "pincode": "400079", "risk_score": 46, "trend": "stable", "lat": 19.1102, "lng": 72.9280},
    {"name": "Mulund", "city": "Mumbai", "state": "Maharashtra", "pincode": "400080", "risk_score": 34, "trend": "improving", "lat": 19.1726, "lng": 72.9561},

    # Bangalore
    {"name": "Koramangala",      "city": "Bangalore",  "state": "Karnataka",   "pincode": "560034", "risk_score": 28, "trend": "improving",  "lat": 12.9352, "lng": 77.6245},
    {"name": "Indiranagar",      "city": "Bangalore",  "state": "Karnataka",   "pincode": "560038", "risk_score": 35, "trend": "stable",     "lat": 12.9784, "lng": 77.6408},
    #up
    {"name": "Agra", "city": "Agra", "state": "Uttar Pradesh", "pincode": "282001", "risk_score": 58, "trend": "stable", "lat": 27.1767, "lng": 78.0081},
    {"name": "Aligarh", "city": "Aligarh", "state": "Uttar Pradesh", "pincode": "202001", "risk_score": 55, "trend": "stable", "lat": 27.8974, "lng": 78.0880},
    {"name": "Prayagraj", "city": "Prayagraj", "state": "Uttar Pradesh", "pincode": "211001", "risk_score": 62, "trend": "stable", "lat": 25.4358, "lng": 81.8463},
    {"name": "Ambedkar Nagar", "city": "Akbarpur", "state": "Uttar Pradesh", "pincode": "224122", "risk_score": 48, "trend": "improving", "lat": 26.4290, "lng": 82.5340},
    {"name": "Amethi", "city": "Gauriganj", "state": "Uttar Pradesh", "pincode": "227409", "risk_score": 43, "trend": "improving", "lat": 26.2060, "lng": 81.6920},
    {"name": "Amroha", "city": "Amroha", "state": "Uttar Pradesh", "pincode": "244221", "risk_score": 51, "trend": "stable", "lat": 28.9036, "lng": 78.4698},
    {"name": "Auraiya", "city": "Auraiya", "state": "Uttar Pradesh", "pincode": "206122", "risk_score": 47, "trend": "stable", "lat": 26.4642, "lng": 79.5091},
    {"name": "Ayodhya", "city": "Ayodhya", "state": "Uttar Pradesh", "pincode": "224123", "risk_score": 52, "trend": "stable", "lat": 26.7922, "lng": 82.1998},
    {"name": "Azamgarh", "city": "Azamgarh", "state": "Uttar Pradesh", "pincode": "276001", "risk_score": 57, "trend": "stable", "lat": 26.0739, "lng": 83.1859},
    {"name": "Baghpat", "city": "Baghpat", "state": "Uttar Pradesh", "pincode": "250609", "risk_score": 54, "trend": "stable", "lat": 28.9443, "lng": 77.2187},
    {"name": "Bahraich", "city": "Bahraich", "state": "Uttar Pradesh", "pincode": "271801", "risk_score": 61, "trend": "worsening", "lat": 27.5743, "lng": 81.5940},
    {"name": "Ballia", "city": "Ballia", "state": "Uttar Pradesh", "pincode": "277001", "risk_score": 56, "trend": "stable", "lat": 25.7580, "lng": 84.1487},
    {"name": "Balrampur", "city": "Balrampur", "state": "Uttar Pradesh", "pincode": "271201", "risk_score": 53, "trend": "stable", "lat": 27.4295, "lng": 82.1854},
    {"name": "Banda", "city": "Banda", "state": "Uttar Pradesh", "pincode": "210001", "risk_score": 59, "trend": "stable", "lat": 25.4760, "lng": 80.3390},
    {"name": "Barabanki", "city": "Barabanki", "state": "Uttar Pradesh", "pincode": "225001", "risk_score": 50, "trend": "stable", "lat": 26.9395, "lng": 81.1838},
    {"name": "Bareilly", "city": "Bareilly", "state": "Uttar Pradesh", "pincode": "243001", "risk_score": 64, "trend": "worsening", "lat": 28.3670, "lng": 79.4304},
    {"name": "Basti", "city": "Basti", "state": "Uttar Pradesh", "pincode": "272001", "risk_score": 52, "trend": "stable", "lat": 26.8177, "lng": 82.7638},
    {"name": "Bhadohi", "city": "Gyanpur", "state": "Uttar Pradesh", "pincode": "221304", "risk_score": 46, "trend": "stable", "lat": 25.3328, "lng": 82.4662},
    {"name": "Bijnor", "city": "Bijnor", "state": "Uttar Pradesh", "pincode": "246701", "risk_score": 58, "trend": "stable", "lat": 29.3724, "lng": 78.1361},
    {"name": "Budaun", "city": "Budaun", "state": "Uttar Pradesh", "pincode": "243601", "risk_score": 60, "trend": "stable", "lat": 28.0362, "lng": 79.1267},

    {"name": "Lucknow", "city": "Lucknow", "state": "Uttar Pradesh", "pincode": "226001", "risk_score": 42, "trend": "improving", "lat": 26.8467, "lng": 80.9462},
    {"name": "Kanpur Nagar", "city": "Kanpur", "state": "Uttar Pradesh", "pincode": "208001", "risk_score": 71, "trend": "worsening", "lat": 26.4499, "lng": 80.3319},
    {"name": "Ghaziabad", "city": "Ghaziabad", "state": "Uttar Pradesh", "pincode": "201001", "risk_score": 74, "trend": "worsening", "lat": 28.6692, "lng": 77.4538},
    {"name": "Noida", "city": "Noida", "state": "Uttar Pradesh", "pincode": "201301", "risk_score": 75, "trend": "stable", "lat": 28.5355, "lng": 77.3910},
    {"name": "Varanasi", "city": "Varanasi", "state": "Uttar Pradesh", "pincode": "221001", "risk_score": 63, "trend": "stable", "lat": 25.3176, "lng": 82.9739},
    {"name": "Gorakhpur", "city": "Gorakhpur", "state": "Uttar Pradesh", "pincode": "273001", "risk_score": 61, "trend": "stable", "lat": 26.7606, "lng": 83.3732},
    {"name": "Meerut", "city": "Meerut", "state": "Uttar Pradesh", "pincode": "250001", "risk_score": 69, "trend": "worsening", "lat": 28.9845, "lng": 77.7064},
    {"name": "Mathura", "city": "Mathura", "state": "Uttar Pradesh", "pincode": "281001", "risk_score": 57, "trend": "stable", "lat": 27.4924, "lng": 77.6737},
    {"name": "Moradabad", "city": "Moradabad", "state": "Uttar Pradesh", "pincode": "244001", "risk_score": 66, "trend": "stable", "lat": 28.8386, "lng": 78.7733},
    {"name": "Saharanpur", "city": "Saharanpur", "state": "Uttar Pradesh", "pincode": "247001", "risk_score": 62, "trend": "stable", "lat": 29.9671, "lng": 77.5510},
    
    {"name": "Ambala", "city": "Ambala", "state": "Haryana", "pincode": "134003", "risk_score": 58, "trend": "stable", "lat": 30.3782, "lng": 76.7767},

    {"name": "Bhiwani", "city": "Bhiwani", "state": "Haryana", "pincode": "127021", "risk_score": 52, "trend": "stable", "lat": 28.7930, "lng": 76.1397},

    {"name": "Charkhi Dadri", "city": "Charkhi Dadri", "state": "Haryana", "pincode": "127306", "risk_score": 46, "trend": "improving", "lat": 28.5921, "lng": 76.2711},

    {"name": "Faridabad", "city": "Faridabad", "state": "Haryana", "pincode": "121001", "risk_score": 72, "trend": "worsening", "lat": 28.4089, "lng": 77.3178},

    {"name": "Fatehabad", "city": "Fatehabad", "state": "Haryana", "pincode": "125050", "risk_score": 49, "trend": "stable", "lat": 29.5152, "lng": 75.4555},

    {"name": "Gurugram", "city": "Gurugram", "state": "Haryana", "pincode": "122001", "risk_score": 68, "trend": "stable", "lat": 28.4595, "lng": 77.0266},

    {"name": "Hisar", "city": "Hisar", "state": "Haryana", "pincode": "125001", "risk_score": 61, "trend": "stable", "lat": 29.1492, "lng": 75.7217},

    {"name": "Jhajjar", "city": "Jhajjar", "state": "Haryana", "pincode": "124103", "risk_score": 50, "trend": "stable", "lat": 28.6063, "lng": 76.6565},

    {"name": "Jind", "city": "Jind", "state": "Haryana", "pincode": "126102", "risk_score": 55, "trend": "stable", "lat": 29.3154, "lng": 76.3150},

    {"name": "Kaithal", "city": "Kaithal", "state": "Haryana", "pincode": "136027", "risk_score": 53, "trend": "stable", "lat": 29.8014, "lng": 76.3996},

    {"name": "Karnal", "city": "Karnal", "state": "Haryana", "pincode": "132001", "risk_score": 59, "trend": "stable", "lat": 29.6857, "lng": 76.9905},

    {"name": "Kurukshetra", "city": "Kurukshetra", "state": "Haryana", "pincode": "136118", "risk_score": 51, "trend": "improving", "lat": 29.9695, "lng": 76.8783},

    {"name": "Mahendragarh", "city": "Narnaul", "state": "Haryana", "pincode": "123001", "risk_score": 47, "trend": "improving", "lat": 28.0444, "lng": 76.1083},

    {"name": "Nuh", "city": "Nuh", "state": "Haryana", "pincode": "122107", "risk_score": 79, "trend": "worsening", "lat": 28.1024, "lng": 77.0017},

    {"name": "Palwal", "city": "Palwal", "state": "Haryana", "pincode": "121102", "risk_score": 63, "trend": "stable", "lat": 28.1447, "lng": 77.3255},

    {"name": "Panchkula", "city": "Panchkula", "state": "Haryana", "pincode": "134109", "risk_score": 32, "trend": "improving", "lat": 30.6942, "lng": 76.8606},

    {"name": "Panipat", "city": "Panipat", "state": "Haryana", "pincode": "132103", "risk_score": 64, "trend": "stable", "lat": 29.3909, "lng": 76.9635},

    {"name": "Rewari", "city": "Rewari", "state": "Haryana", "pincode": "123401", "risk_score": 57, "trend": "stable", "lat": 28.1979, "lng": 76.6176},

    {"name": "Rohtak", "city": "Rohtak", "state": "Haryana", "pincode": "124001", "risk_score": 62, "trend": "stable", "lat": 28.8955, "lng": 76.6066},

    {"name": "Sirsa", "city": "Sirsa", "state": "Haryana", "pincode": "125055", "risk_score": 56, "trend": "stable", "lat": 29.5349, "lng": 75.0289},

    {"name": "Sonipat", "city": "Sonipat", "state": "Haryana", "pincode": "131001", "risk_score": 67, "trend": "worsening", "lat": 28.9931, "lng": 77.0151},

    {"name": "Yamunanagar", "city": "Yamunanagar", "state": "Haryana", "pincode": "135001", "risk_score": 54, "trend": "stable", "lat": 30.1290, "lng": 77.2674},

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
