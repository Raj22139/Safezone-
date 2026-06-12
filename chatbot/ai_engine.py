"""
SafeZone AI Chatbot — AI Fallback Engine
Uses Anthropic Claude API when rule-based engine has no match.
"""

import json
import urllib.request
import urllib.error
from django.conf import settings


SYSTEM_PROMPT = """You are SafeZone AI Assistant — a helpful chatbot for the SafeZone AI Crime and Area Safety Intelligence System.

About the system:
- SafeZone AI analyzes crime data for any area and gives a Risk Score (0-100)
- Risk Levels: Low (0-35), Medium (36-65), High (66-100)
- It uses a Scikit-learn RandomForest ML model for risk prediction
- Users can search areas, view crime breakdowns, and get safer area suggestions
- Built with Django + PostgreSQL backend

Your role:
- Answer questions about area safety, crime prevention, and how the system works
- Give practical safety advice
- Be friendly, concise, and helpful
- Use emojis naturally to make responses engaging
- Keep responses under 150 words
- If asked about a specific area's safety, suggest the user search it on the dashboard
- Do NOT make up specific crime statistics — guide users to search on the platform

Always respond in the same language the user writes in (Hindi/English/Hinglish)."""


def get_ai_response(user_message: str, conversation_history: list = None) -> tuple:
    """
    Call Claude API for AI-powered response.
    Returns (response_text, source) where source is 'ai' or 'error'.
    """
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    if not api_key:
        return _fallback_response(), 'error'

    messages = []

    # Include recent conversation history (last 6 messages for context)
    if conversation_history:
        for msg in conversation_history[-6:]:
            messages.append({
                'role': msg['role'] if msg['role'] == 'user' else 'assistant',
                'content': msg['content']
            })

    # Add current message
    messages.append({'role': 'user', 'content': user_message})

    payload = json.dumps({
        'model': 'claude-haiku-4-5-20251001',
        'max_tokens': 300,
        'system': SYSTEM_PROMPT,
        'messages': messages,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=payload,
        headers={
            'Content-Type':      'application/json',
            'x-api-key':         api_key,
            'anthropic-version': '2023-06-01',
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            text = data['content'][0]['text']
            return text, 'ai'
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return _fallback_response(), 'error'
    except Exception:
        return _fallback_response(), 'error'


def _fallback_response() -> str:
    return (
        "🤔 I'm not sure about that specific question.\n\n"
        "Here's what I can help with:\n"
        "- 🔍 **Area safety checks** — Search any location\n"
        "- 📊 **Risk scores** — Understanding Low/Medium/High\n"
        "- 🛡️ **Safety tips** — Stay safe in any area\n"
        "- ℹ️ **How it works** — About SafeZone AI\n\n"
        "Try asking: *'How does risk score work?'* or *'Safety tips'*"
    )
