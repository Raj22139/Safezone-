"""
Management command: python manage.py run_telegram_bot
Starts the SafeZone AI Telegram bot.
"""
import asyncio
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run SafeZone AI Telegram Bot'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting SafeZone AI Telegram Bot...'))
        from chatbot.telegram_bot import run_bot
        asyncio.run(run_bot())
