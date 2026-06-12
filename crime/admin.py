from django.contrib import admin
from .models import Area, CrimeRecord, SearchHistory, SavedArea


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display  = ['name', 'city', 'risk_score', 'risk_level', 'trend', 'is_active']
    list_filter   = ['risk_level', 'city', 'is_active', 'trend']
    search_fields = ['name', 'city', 'pincode']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CrimeRecord)
class CrimeRecordAdmin(admin.ModelAdmin):
    list_display  = ['area', 'crime_type', 'severity', 'incident_date', 'status']
    list_filter   = ['crime_type', 'status', 'severity']
    search_fields = ['area__name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display  = ['user', 'query', 'risk_score', 'risk_level', 'searched_at']
    list_filter   = ['risk_level']
    readonly_fields = ['searched_at']


@admin.register(SavedArea)
class SavedAreaAdmin(admin.ModelAdmin):
    list_display = ['user', 'area', 'saved_at']


# New models
try:
    from .models import AreaReview, AlertSubscription, CrimeReport, SOSAlert, SafetyJourney, AnonymousTip, RouteSearch

    @admin.register(AreaReview)
    class AreaReviewAdmin(admin.ModelAdmin):
        list_display = ['area', 'user', 'rating', 'is_approved', 'created_at']
        list_filter  = ['is_approved', 'rating']

    @admin.register(AlertSubscription)
    class AlertSubscriptionAdmin(admin.ModelAdmin):
        list_display = ['user', 'area', 'alert_type', 'is_active']

    @admin.register(CrimeReport)
    class CrimeReportAdmin(admin.ModelAdmin):
        list_display = ['location_text', 'crime_type', 'severity', 'status', 'reported_by', 'created_at']
        list_filter  = ['status', 'crime_type']

    @admin.register(SOSAlert)
    class SOSAlertAdmin(admin.ModelAdmin):
        list_display = ['user', 'location_text', 'is_resolved', 'created_at']

    @admin.register(AnonymousTip)
    class AnonymousTipAdmin(admin.ModelAdmin):
        list_display = ['location_text', 'crime_type', 'status', 'upvotes', 'created_at']

    @admin.register(RouteSearch)
    class RouteSearchAdmin(admin.ModelAdmin):
        list_display = ['user', 'origin', 'destination', 'risk_level', 'searched_at']

except Exception:
    pass  # Models may not exist yet before migration
