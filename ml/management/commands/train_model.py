"""
Management command: python manage.py train_model
Trains the Scikit-learn risk scoring model and saves it.
"""

from django.core.management.base import BaseCommand
from ml.risk_engine import train_and_save_model


class Command(BaseCommand):
    help = 'Train and save the SafeZone AI risk scoring ML model'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('[SafeZone AI] Training ML model...'))
        train_and_save_model()
        self.stdout.write(self.style.SUCCESS('[SafeZone AI] Model trained and saved successfully!'))
