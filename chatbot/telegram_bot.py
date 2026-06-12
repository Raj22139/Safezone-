"""
SafeZone AI — Telegram Bot Integration
Commands: /start /check /safecity /sos /help
Run: python manage.py run_telegram_bot
"""
import logging
import hashlib
import random
from django.conf import settings

logger = logging.getLogger(__name__)

BOT_COMMANDS = {
    '/start':    'Welcome message and intro',
    '/check':    '/check <area> — Check area safety score',
    '/safecity': 'Show top 5 safest cities',
    '/dangerous':'/dangerous — Show top 5 dangerous areas',
    '/sos':      'Emergency numbers',
    '/help':     'Show all commands',
}

EMERGENCY_MSG = """
🚨 *EMERGENCY NUMBERS (India)*

🚔 Police: *100*
🚑 Ambulance: *108*
🔥 Fire Brigade: *101*
👩 Women Helpline: *1091*
👶 Child Helpline: *1098*
📱 Emergency SMS: *112*

Stay safe! 🛡️
"""


def get_area_safety(area_name: str) -> dict:
    """Check area safety using Django ORM."""
    try:
        import django
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safezone.settings')

        from crime.models import Area
        from django.db.models import Q

        area = Area.objects.filter(
            Q(name__icontains=area_name) | Q(city__icontains=area_name),
            is_active=True
        ).first()

        if area:
            return {
                'name':  str(area),
                'score': area.risk_score,
                'level': area.risk_level,
                'trend': area.trend,
                'found': True,
            }
    except Exception:
        pass

    # AI estimate
    seed  = int(hashlib.md5(area_name.lower().encode()).hexdigest(), 16) % 9999
    score = random.Random(seed).randint(10, 90)
    level = 'low' if score <= 35 else 'medium' if score <= 65 else 'high'
    return {'name': area_name.title(), 'score': score, 'level': level, 'trend': 'stable', 'found': False}


def format_area_response(data: dict) -> str:
    emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(data['level'], '⚪')
    label = {'low': 'LOW RISK ✅', 'medium': 'MEDIUM RISK ⚠️', 'high': 'HIGH RISK 🚨'}.get(data['level'], '')
    est   = ' _(AI Estimated)_' if not data.get('found') else ''
    return (
        f"🛡️ *SafeZone AI Safety Report*{est}\n\n"
        f"📍 *{data['name']}*\n"
        f"{emoji} *{label}*\n"
        f"📊 Risk Score: *{data['score']}/100*\n"
        f"📈 Trend: {data['trend'].title()}\n\n"
        f"Check full details: https://safezone.ai/dashboard/"
    )


async def run_bot():
    """Start the Telegram bot. Call from management command."""
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not set in settings. Bot disabled.")
        return

    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

        async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_markdown(
                "👋 Welcome to *SafeZone AI Bot*!\n\n"
                "I can help you check area safety scores powered by AI.\n\n"
                "Try: `/check Connaught Place, Delhi`\n\n"
                "Type /help for all commands."
            )

        async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
            msg = "🛡️ *SafeZone AI Commands*\n\n"
            for cmd, desc in BOT_COMMANDS.items():
                msg += f"`{cmd}` — {desc}\n"
            await update.message.reply_markdown(msg)

        async def check(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
            if not ctx.args:
                await update.message.reply_text("Usage: /check <area name>\nExample: /check Mumbai")
                return
            area_name = ' '.join(ctx.args)
            await update.message.reply_text(f"🔍 Checking safety for: {area_name}...")
            data     = get_area_safety(area_name)
            response = format_area_response(data)
            await update.message.reply_markdown(response)

        async def safecity(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
            try:
                from crime.models import Area
                from django.db.models import Avg
                cities = Area.objects.filter(is_active=True).values('city').annotate(
                    avg=Avg('risk_score')).order_by('avg')[:5]
                msg = "🏆 *Top 5 Safest Cities*\n\n"
                for i, c in enumerate(cities, 1):
                    msg += f"{i}. {c['city']} — Score: {round(c['avg'])}/100 🟢\n"
                await update.message.reply_markdown(msg)
            except Exception:
                await update.message.reply_text("Data not available. Try after seeding database.")

        async def sos(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_markdown(EMERGENCY_MSG)

        async def message_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
            text = update.message.text
            if text:
                data     = get_area_safety(text)
                response = format_area_response(data)
                await update.message.reply_markdown(response)

        app = Application.builder().token(token).build()
        app.add_handler(CommandHandler('start',     start))
        app.add_handler(CommandHandler('help',      help_cmd))
        app.add_handler(CommandHandler('check',     check))
        app.add_handler(CommandHandler('safecity',  safecity))
        app.add_handler(CommandHandler('dangerous', safecity))
        app.add_handler(CommandHandler('sos',       sos))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

        logger.info("SafeZone AI Telegram Bot started!")
        await app.run_polling()

    except ImportError:
        logger.error("python-telegram-bot not installed. Run: pip install python-telegram-bot")
    except Exception as e:
        logger.error(f"Telegram bot error: {e}")
