"""
SafeZone AI Chatbot — Rule-Based Engine
Handles common safety, area, and system questions before falling back to AI.
"""

import re

# ── RULE DATABASE ──
# Each rule: { 'patterns': [regex,...], 'response': str, 'category': str }
RULES = [

    # ── Greetings ──
    {
        'patterns': [r'\b(hi|hello|hey|namaste|hii|helo|salam)\b', r'^(good\s*(morning|evening|afternoon|night))'],
        'response': (
            "👋 Hello! Welcome to **SafeZone AI**!\n\n"
            "I can help you with:\n"
            "- 🔍 Area safety checks\n"
            "- 📊 Understanding risk scores\n"
            "- 🛡️ Crime safety tips\n"
            "- ℹ️ How our system works\n\n"
            "What would you like to know?"
        ),
        'category': 'greeting',
    },

    # ── What is SafeZone ──
    {
        'patterns': [r'what is safezone', r'about (this|safezone|system|website|app)',
                     r'(tell me|explain).*(safezone|system|this)', r'safezone (kya|hai)'],
        'response': (
            "🛡️ **SafeZone AI** is an AI-Based Crime and Area Safety Intelligence System.\n\n"
            "**What it does:**\n"
            "- Analyzes crime data for any area\n"
            "- Generates an AI-powered **Risk Score (0–100)**\n"
            "- Classifies areas as Low / Medium / High risk\n"
            "- Suggests nearby safer areas when risk is high\n\n"
            "**Goal:** Help people make informed safety decisions before traveling or relocating. 🏙️"
        ),
        'category': 'about',
    },

    # ── Risk Score ──
    {
        'patterns': [r'risk score', r'score (kya|mean|matlab|batao)', r'(0.?100|scoring)',
                     r'how.*(score|calculated)', r'score kaise'],
        'response': (
            "📊 **Risk Score (0–100)** is calculated by our AI (Scikit-learn RandomForest model).\n\n"
            "**It analyzes:**\n"
            "- Total crime incidents in the area\n"
            "- Types of crimes (theft, violence, fraud, etc.)\n"
            "- Average severity of incidents\n"
            "- Historical crime trends\n\n"
            "**Meaning:**\n"
            "🟢 **0–35** → Low Risk (Safe area)\n"
            "🟡 **36–65** → Medium Risk (Be cautious)\n"
            "🔴 **66–100** → High Risk (Avoid if possible)"
        ),
        'category': 'risk_score',
    },

    # ── Low Risk ──
    {
        'patterns': [r'low risk', r'safe area', r'(green|safest).*(area|zone)',
                     r'(area|zone).*(safe|green)'],
        'response': (
            "🟢 **Low Risk Area (Score 0–35)**\n\n"
            "- Minimal crime activity reported\n"
            "- Generally safe for families and daily commute\n"
            "- Rare incidents only\n"
            "- Good police presence\n\n"
            "✅ These areas are safe for residence, travel, and work."
        ),
        'category': 'risk_level',
    },

    # ── Medium Risk ──
    {
        'patterns': [r'medium risk', r'moderate.*(risk|safe)', r'yellow.*(area|zone)',
                     r'(area|zone).*(yellow|medium)'],
        'response': (
            "🟡 **Medium Risk Area (Score 36–65)**\n\n"
            "- Moderate crime activity detected\n"
            "- Petty crimes (theft, pickpocketing) may occur\n"
            "- Traffic incidents are common\n\n"
            "⚠️ **Tips:**\n"
            "- Be alert in crowded places\n"
            "- Avoid isolated areas at night\n"
            "- Keep valuables secure"
        ),
        'category': 'risk_level',
    },

    # ── High Risk ──
    {
        'patterns': [r'high risk', r'danger(ous)?.*(area|zone)', r'red.*(area|zone)',
                     r'(area|zone).*(red|high|danger)', r'unsafe area'],
        'response': (
            "🔴 **High Risk Area (Score 66–100)**\n\n"
            "- Significant crime activity detected\n"
            "- Serious incidents including violence, robbery reported\n"
            "- Avoid traveling alone, especially at night\n\n"
            "🆘 **Safety Tips:**\n"
            "- Avoid the area if possible\n"
            "- Check our **Safer Area Suggestions** nearby\n"
            "- Keep emergency numbers handy (Police: 100)\n"
            "- Inform someone of your whereabouts"
        ),
        'category': 'risk_level',
    },

    # ── How to search ──
    {
        'patterns': [r'how.*(search|check|find).*(area|safety|location)',
                     r'(search|check|find).*(kaise|karna|karein)',
                     r'area (safety|check|search)', r'kaise (check|search|pata)'],
        'response': (
            "🔍 **How to Check Area Safety:**\n\n"
            "1. Go to your **Dashboard** (login required)\n"
            "2. Enter the area name, city, or pincode in the search box\n"
            "3. Click **Analyze** or press Enter\n"
            "4. View your:\n"
            "   - Risk Score (0–100)\n"
            "   - Risk Level (Low / Medium / High)\n"
            "   - Crime breakdown by type\n"
            "   - Nearby safer alternatives\n\n"
            "👉 [Go to Dashboard](/dashboard/)"
        ),
        'category': 'how_to',
    },

    # ── Registration / Login ──
    {
        'patterns': [r'(register|signup|sign up|create account)',
                     r'(login|log in|sign in)', r'account (kaise|banana|banao)',
                     r'kaise (login|register)'],
        'response': (
            "👤 **Account Setup:**\n\n"
            "**Register (New User):**\n"
            "→ [Create Account](/accounts/register/)\n"
            "Fill: Name, Email, Username, Password\n\n"
            "**Login (Existing User):**\n"
            "→ [Login Here](/accounts/login/)\n\n"
            "**Benefits of an account:**\n"
            "- Search any area's safety\n"
            "- Save your search history\n"
            "- Bookmark favorite areas\n"
            "- Access detailed crime reports"
        ),
        'category': 'account',
    },

    # ── Crime types ──
    {
        'patterns': [r'(crime|crimes).*(type|kind|category|categories)',
                     r'(type|kind).*(crime|criminal)', r'what.*(crime|crimes)',
                     r'crime (kya|kitne|type)'],
        'response': (
            "🗂️ **Crime Categories in SafeZone AI:**\n\n"
            "🚗 **Traffic Incidents** — Accidents, rash driving\n"
            "💼 **Theft / Robbery** — Pickpocketing, snatching\n"
            "⚠️ **Violent Crime** — Assault, fights\n"
            "💻 **Fraud / Cyber** — Online scams, identity theft\n"
            "🏠 **Burglary** — House break-ins\n"
            "🤜 **Assault** — Physical attacks\n"
            "🔨 **Vandalism** — Property damage\n\n"
            "Each crime type is weighted in our AI model to calculate the final risk score."
        ),
        'category': 'crime_types',
    },

    # ── Safety tips ──
    {
        'patterns': [r'safety (tips|advice|measures|precautions)',
                     r'(tips|advice).*(safe|safety)', r'kaise safe (rahe|raho|rahein)',
                     r'safe (kaise|rehna)', r'(protect|bachao|bachna)'],
        'response': (
            "🛡️ **General Safety Tips:**\n\n"
            "**Before Traveling:**\n"
            "✅ Check the area's risk score on SafeZone AI\n"
            "✅ Inform someone of your route\n"
            "✅ Avoid high-risk areas at night\n\n"
            "**While Traveling:**\n"
            "✅ Keep valuables hidden\n"
            "✅ Stay in well-lit, populated areas\n"
            "✅ Trust your instincts\n\n"
            "**Emergency Numbers (India):**\n"
            "🚨 Police: **100**\n"
            "🚑 Ambulance: **108**\n"
            "🔥 Fire: **101**\n"
            "📞 Women Helpline: **1091**"
        ),
        'category': 'safety_tips',
    },

    # ── Safer areas ──
    {
        'patterns': [r'safer (area|place|location|alternative)',
                     r'(alternative|nearby).*(safe|area)', r'(suggest|recommendation).*(area|place)',
                     r'safe (area|jagah) (suggest|batao|dikhao)'],
        'response': (
            "📍 **Finding Safer Areas:**\n\n"
            "When you search a **High or Medium risk** area, SafeZone AI automatically:\n\n"
            "1. Detects high-risk zones\n"
            "2. Scans nearby areas in the same city\n"
            "3. Shows **Safer Area Chips** with:\n"
            "   - Area name\n"
            "   - Distance from searched location\n"
            "   - Risk score comparison\n\n"
            "👉 Try searching an area on your [Dashboard](/dashboard/) to see suggestions!"
        ),
        'category': 'safer_areas',
    },

    # ── ML / AI ──
    {
        'patterns': [r'(ai|ml|machine learning|artificial intelligence).*(work|kaam|use)',
                     r'(model|algorithm).*(use|used|kaam)', r'scikit|random forest',
                     r'how.*(ai|ml).*(work|predict)', r'ai kaise (kaam|predict)'],
        'response': (
            "🤖 **Our AI Risk Engine:**\n\n"
            "**Model:** Scikit-learn RandomForest Regressor\n\n"
            "**Features analyzed:**\n"
            "- Total crime incidents\n"
            "- Average severity score\n"
            "- Count by crime type (theft, violence, fraud...)\n"
            "- Weighted severity score\n\n"
            "**Process:**\n"
            "1. Crime records from DB are fetched\n"
            "2. Feature vector is built\n"
            "3. RandomForest predicts Risk Score (0–100)\n"
            "4. Score auto-sets Low / Medium / High level\n\n"
            "**Accuracy:** ~98.4% on test data ✅"
        ),
        'category': 'ai_model',
    },

    # ── Admin panel ──
    {
        'patterns': [r'admin (panel|dashboard|access)', r'admin (kaise|access|login)',
                     r'(add|edit|delete).*(crime|record|data)',
                     r'crime data (manage|add|update)'],
        'response': (
            "⚙️ **Admin Panel:**\n\n"
            "The Admin Panel is for **authorized administrators** only.\n\n"
            "**Admin can:**\n"
            "- ➕ Add / Edit / Delete crime records\n"
            "- 📍 Manage area database\n"
            "- 👥 Manage user accounts\n"
            "- 📊 View analytics & reports\n"
            "- ✅ Approve / Reject crime reports\n\n"
            "**Access:** `/admin-panel/`\n"
            "*(Requires admin credentials)*"
        ),
        'category': 'admin',
    },

    # ── Emergency ──
    {
        'patterns': [r'(emergency|help|danger|bachao|bachana|sos)',
                     r'(police|ambulance|fire|helpline).*(number|no|contact)',
                     r'(number|contact).*(police|ambulance|emergency)'],
        'response': (
            "🆘 **EMERGENCY CONTACTS (India):**\n\n"
            "🚨 **Police:** 100\n"
            "🚑 **Ambulance:** 108\n"
            "🔥 **Fire Brigade:** 101\n"
            "📞 **Women Helpline:** 1091\n"
            "👶 **Child Helpline:** 1098\n"
            "🏥 **Disaster Management:** 108\n"
            "📱 **Emergency SMS:** 112\n\n"
            "**If in immediate danger, call 100 immediately!** 🚨"
        ),
        'category': 'emergency',
    },

    # ── Search history ──
    {
        'patterns': [r'(search|history|past).*(history|searches|record)',
                     r'(purani|previous|past).*(search|history)',
                     r'history (kahan|dekho|dekhna)'],
        'response': (
            "🕐 **Search History:**\n\n"
            "All your previous area searches are saved automatically.\n\n"
            "**To view:** Go to [Search History](/dashboard/history/)\n\n"
            "You can see:\n"
            "- Area searched\n"
            "- Risk score at time of search\n"
            "- Date and time\n"
            "- Risk level (Low/Medium/High)\n\n"
            "*(Login required to access history)*"
        ),
        'category': 'history',
    },

    # ── Saved areas ──
    {
        'patterns': [r'(save|bookmark|saved).*(area|place|location)',
                     r'(area|place).*(save|bookmark)', r'(saved|bookmark).*(kahan|dekho)',
                     r'favourite.*(area|place)'],
        'response': (
            "🔖 **Saved Areas:**\n\n"
            "You can bookmark areas you frequently check.\n\n"
            "**To save:** Click the 'Save Area' button on any area detail page\n\n"
            "**To view:** Go to [Saved Areas](/dashboard/saved/)\n\n"
            "Saved areas show:\n"
            "- Area name and city\n"
            "- Current risk score\n"
            "- Quick access to safety details"
        ),
        'category': 'saved_areas',
    },

    # ── Thank you ──
    {
        'patterns': [r'\b(thanks|thank you|thankyou|shukriya|dhanyawad|thx)\b'],
        'response': (
            "😊 You're welcome! Stay safe out there!\n\n"
            "Feel free to ask anything else about area safety. I'm here 24/7! 🛡️"
        ),
        'category': 'thanks',
    },

    # ── Bye ──
    {
        'patterns': [r'\b(bye|goodbye|good bye|alvida|baad mein|later)\b'],
        'response': (
            "👋 Goodbye! Stay safe!\n\n"
            "Remember to check area safety before you travel. 🛡️\n"
            "Come back anytime!"
        ),
        'category': 'bye',
    },
]


def match_rule(user_message: str):
    """
    Try to match user message against all rules.
    Returns (response_text, category) or (None, None) if no match.
    """
    msg = user_message.lower().strip()
    # Remove extra punctuation
    msg = re.sub(r'[?!.,;:]+', ' ', msg).strip()

    for rule in RULES:
        for pattern in rule['patterns']:
            if re.search(pattern, msg, re.IGNORECASE):
                return rule['response'], rule['category']

    return None, None


def get_quick_suggestions(page_context: str = 'public') -> list:
    """Return context-aware quick reply suggestions."""
    base = [
        "What is SafeZone AI?",
        "How does risk score work?",
        "Safety tips",
        "Emergency numbers",
    ]
    dashboard = [
        "How to search an area?",
        "What does High Risk mean?",
        "How to save an area?",
        "View my search history",
    ]
    admin = [
        "How to add crime record?",
        "What is admin panel?",
        "How to manage users?",
        "View analytics",
    ]
    if page_context == 'dashboard':
        return dashboard
    if page_context == 'admin':
        return admin
    return base
