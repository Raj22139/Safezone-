"""
SafeZone AI — REST API Serializers
"""
from rest_framework import serializers
from crime.models import Area, CrimeRecord, SearchHistory
from django.contrib.auth.models import User


class AreaSerializer(serializers.ModelSerializer):
    risk_label = serializers.ReadOnlyField()
    risk_color = serializers.ReadOnlyField()

    class Meta:
        model  = Area
        fields = ['id','name','city','state','pincode','risk_score',
                  'risk_level','risk_label','risk_color','trend',
                  'description','latitude','longitude','is_active',
                  'created_at','updated_at']
        read_only_fields = ['risk_level','created_at','updated_at']


class CrimeRecordSerializer(serializers.ModelSerializer):
    area_name      = serializers.CharField(source='area.name', read_only=True)
    city           = serializers.CharField(source='area.city', read_only=True)
    crime_type_label = serializers.CharField(source='get_crime_type_display', read_only=True)

    class Meta:
        model  = CrimeRecord
        fields = ['id','area','area_name','city','crime_type','crime_type_label',
                  'description','incident_date','severity','status','created_at']
        read_only_fields = ['created_at']


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = SearchHistory
        fields = ['id','query','area','risk_score','risk_level','searched_at']
        read_only_fields = ['searched_at']


class AreaRiskSummarySerializer(serializers.Serializer):
    """Serializer for AI risk analysis result."""
    area_id     = serializers.IntegerField()
    area_name   = serializers.CharField()
    score       = serializers.IntegerField()
    level       = serializers.CharField()
    description = serializers.CharField()
    estimated   = serializers.BooleanField()
    crime_types = serializers.DictField(child=serializers.IntegerField())
    safer_areas = serializers.ListField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id','username','first_name','last_name','email','date_joined']
        read_only_fields = ['date_joined']
