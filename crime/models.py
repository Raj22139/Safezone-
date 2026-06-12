from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Area(models.Model):
    """Represents a geographic area with its risk profile."""

    RISK_LEVEL_CHOICES = [
        ('low',    'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high',   'High Risk'),
    ]

    TREND_CHOICES = [
        ('improving',  'Improving'),
        ('stable',     'Stable'),
        ('worsening',  'Worsening'),
    ]

    name        = models.CharField(max_length=150)
    city        = models.CharField(max_length=100)
    state       = models.CharField(max_length=100, blank=True, null=True)
    pincode     = models.CharField(max_length=10, blank=True, null=True)
    latitude    = models.DecimalField(max_digits=9,  decimal_places=6, blank=True, null=True)
    longitude   = models.DecimalField(max_digits=9,  decimal_places=6, blank=True, null=True)
    risk_score  = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    risk_level  = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES, default='low')
    trend       = models.CharField(max_length=15, choices=TREND_CHOICES, default='stable')
    description = models.TextField(blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Area'
        verbose_name_plural = 'Areas'
        ordering            = ['-risk_score']
        unique_together     = ['name', 'city']

    def __str__(self):
        return f"{self.name}, {self.city}"

    def save(self, *args, **kwargs):
        """Auto-set risk_level based on risk_score."""
        if self.risk_score <= 35:
            self.risk_level = 'low'
        elif self.risk_score <= 65:
            self.risk_level = 'medium'
        else:
            self.risk_level = 'high'
        super().save(*args, **kwargs)

    @property
    def risk_color(self):
        return {'low': '#00C48C', 'medium': '#F59E0B', 'high': '#EF4444'}.get(self.risk_level, '#6B7594')

    @property
    def risk_label(self):
        return {'low': 'Low Risk', 'medium': 'Medium Risk', 'high': 'High Risk'}.get(self.risk_level)


class CrimeRecord(models.Model):
    """Individual crime incident record for an area."""

    CRIME_TYPE_CHOICES = [
        ('theft',     'Theft / Robbery'),
        ('violence',  'Violent Crime'),
        ('traffic',   'Traffic Incident'),
        ('fraud',     'Fraud / Cyber Crime'),
        ('burglary',  'Burglary'),
        ('assault',   'Assault'),
        ('vandalism', 'Vandalism'),
        ('other',     'Other'),
    ]

    STATUS_CHOICES = [
        ('pending',  'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    area         = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='crime_records')
    crime_type   = models.CharField(max_length=20, choices=CRIME_TYPE_CHOICES)
    description  = models.TextField()
    incident_date= models.DateField()
    severity     = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="1=Minor, 10=Extreme"
    )
    reported_by  = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reported_crimes'
    )
    added_by_admin = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='admin_added_crimes'
    )
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Crime Record'
        verbose_name_plural = 'Crime Records'
        ordering            = ['-incident_date', '-created_at']

    def __str__(self):
        return f"{self.get_crime_type_display()} — {self.area.name} ({self.incident_date})"


class SearchHistory(models.Model):
    """Stores every area safety search a user performs."""

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    query       = models.CharField(max_length=200)          # raw search string
    area        = models.ForeignKey(
        Area, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='searches'
    )
    risk_score  = models.IntegerField(null=True, blank=True)
    risk_level  = models.CharField(max_length=10, blank=True, null=True)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Search History'
        verbose_name_plural = 'Search Histories'
        ordering            = ['-searched_at']

    def __str__(self):
        return f"{self.user.username} searched '{self.query}'"


class SavedArea(models.Model):
    """Areas bookmarked by a user."""

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_areas')
    area       = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='saved_by')
    saved_at   = models.DateTimeField(auto_now_add=True)
    notes      = models.TextField(blank=True, null=True)

    class Meta:
        unique_together     = ['user', 'area']
        ordering            = ['-saved_at']
        verbose_name        = 'Saved Area'
        verbose_name_plural = 'Saved Areas'

    def __str__(self):
        return f"{self.user.username} saved {self.area.name}"


class AreaReview(models.Model):
    """User reviews and ratings for areas."""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    area        = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='reviews')
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating      = models.IntegerField(choices=RATING_CHOICES)
    comment     = models.TextField(max_length=500)
    is_approved = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['area', 'user']
        ordering        = ['-created_at']

    def __str__(self):
        return f"{self.user.username} rated {self.area.name} — {self.rating}/5"


class AlertSubscription(models.Model):
    """Email alert subscriptions for areas."""
    ALERT_TYPES = [
        ('high_risk',   'High Risk Alert'),
        ('any_change',  'Any Risk Change'),
        ('weekly',      'Weekly Summary'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alert_subscriptions')
    area       = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='subscribers')
    alert_type = models.CharField(max_length=15, choices=ALERT_TYPES, default='high_risk')
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'area', 'alert_type']

    def __str__(self):
        return f"{self.user.username} → {self.area.name} [{self.alert_type}]"


class CrimeReport(models.Model):
    """User-submitted crime reports."""
    STATUS_CHOICES = [
        ('pending',  'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    area          = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='user_reports', null=True, blank=True)
    reported_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='crime_reports')
    crime_type    = models.CharField(max_length=20, choices=CrimeRecord.CRIME_TYPE_CHOICES)
    description   = models.TextField()
    location_text = models.CharField(max_length=200)
    incident_date = models.DateField()
    severity      = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    photo         = models.ImageField(upload_to='crime_reports/', blank=True, null=True)
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    whatsapp_sent = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report: {self.crime_type} @ {self.location_text}"


class RouteSearch(models.Model):
    """Saved route safety searches."""
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='route_searches')
    origin     = models.CharField(max_length=200)
    destination= models.CharField(max_length=200)
    risk_score = models.IntegerField(default=0)
    risk_level = models.CharField(max_length=10, default='low')
    searched_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-searched_at']

    def __str__(self):
        return f"{self.origin} → {self.destination}"


class SOSAlert(models.Model):
    """Emergency SOS alerts sent by users."""
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sos_alerts')
    latitude    = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude   = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_text = models.CharField(max_length=200, blank=True)
    message     = models.TextField(blank=True, default='Emergency! I need help!')
    is_resolved = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"SOS by {self.user.username} at {self.created_at:%Y-%m-%d %H:%M}"


class SafetyJourney(models.Model):
    """Tracks a user's journey for real-time safety monitoring."""
    STATUS_CHOICES = [
        ('active',    'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journeys')
    origin      = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    started_at  = models.DateTimeField(auto_now_add=True)
    ended_at    = models.DateTimeField(null=True, blank=True)
    notes       = models.TextField(blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username}: {self.origin} → {self.destination}"


class AnonymousTip(models.Model):
    """Anonymous crime tips from public."""
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('reviewed', 'Reviewed'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    area          = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)
    crime_type    = models.CharField(max_length=20, choices=CrimeRecord.CRIME_TYPE_CHOICES)
    description   = models.TextField()
    location_text = models.CharField(max_length=200)
    incident_date = models.DateField()
    severity      = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    tip_hash      = models.CharField(max_length=64, unique=True)  # for dedup without identity
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    upvotes       = models.IntegerField(default=0)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Tip: {self.crime_type} @ {self.location_text}"
