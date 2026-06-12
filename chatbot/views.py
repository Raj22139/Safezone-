import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import ChatSession, ChatMessage
from .rules import match_rule, get_quick_suggestions
from .ai_engine import get_ai_response


def _get_or_create_session(request, page_context='public'):
    """Get existing session or create new one for this user/visitor."""
    if request.user.is_authenticated:
        session = ChatSession.objects.filter(
            user=request.user,
            page_context=page_context
        ).order_by('-updated_at').first()
        if not session:
            session = ChatSession.objects.create(
                user=request.user,
                page_context=page_context
            )
    else:
        # Anonymous — use Django session key
        if not request.session.session_key:
            request.session.create()
        key = request.session.session_key
        session = ChatSession.objects.filter(
            session_key=key,
            page_context=page_context
        ).order_by('-updated_at').first()
        if not session:
            session = ChatSession.objects.create(
                session_key=key,
                page_context=page_context
            )
    return session


@require_POST
def chat_message(request):
    """
    POST /chatbot/message/
    Body: { "message": "...", "context": "public|dashboard|admin", "session_id": optional }
    Returns: { "response": "...", "source": "rule|ai|error", "session_id": int }
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_message = data.get('message', '').strip()
    page_context = data.get('context', 'public')
    session_id   = data.get('session_id')

    if not user_message:
        return JsonResponse({'error': 'Message is empty.'}, status=400)

    if len(user_message) > 500:
        return JsonResponse({'error': 'Message too long.'}, status=400)

    # Get / create session
    if session_id:
        try:
            session = ChatSession.objects.get(id=session_id)
        except ChatSession.DoesNotExist:
            session = _get_or_create_session(request, page_context)
    else:
        session = _get_or_create_session(request, page_context)

    # Save user message
    ChatMessage.objects.create(
        session=session,
        role='user',
        content=user_message,
        source='rule'
    )

    # ── Step 1: Try rule-based engine ──
    response_text, category = match_rule(user_message)
    source = 'rule'

    # ── Step 2: AI fallback if no rule matched ──
    if response_text is None:
        # Build conversation history for context
        recent_msgs = session.messages.order_by('-timestamp')[:10]
        history = [
            {'role': m.role if m.role == 'user' else 'assistant', 'content': m.content}
            for m in reversed(recent_msgs)
        ]
        response_text, source = get_ai_response(user_message, history)

    # Save bot response
    ChatMessage.objects.create(
        session=session,
        role='bot',
        content=response_text,
        source=source
    )

    return JsonResponse({
        'response':   response_text,
        'source':     source,
        'session_id': session.id,
        'category':   category or 'ai',
    })


def chat_history(request):
    """GET /chatbot/history/?context=dashboard — Returns last 20 messages."""
    page_context = request.GET.get('context', 'public')
    session = _get_or_create_session(request, page_context)
    messages = session.messages.order_by('timestamp')[:20]
    return JsonResponse({
        'session_id': session.id,
        'messages': [
            {
                'role':      m.role,
                'content':   m.content,
                'source':    m.source,
                'timestamp': m.timestamp.strftime('%H:%M'),
            }
            for m in messages
        ]
    })


def chat_suggestions(request):
    """GET /chatbot/suggestions/?context=dashboard — Quick reply chips."""
    page_context = request.GET.get('context', 'public')
    suggestions  = get_quick_suggestions(page_context)
    return JsonResponse({'suggestions': suggestions})


def chat_clear(request):
    """POST /chatbot/clear/ — Clear current session."""
    if request.method == 'POST':
        page_context = request.POST.get('context', 'public')
        session = _get_or_create_session(request, page_context)
        session.messages.all().delete()
        return JsonResponse({'status': 'cleared'})
    return JsonResponse({'error': 'POST required'}, status=405)
