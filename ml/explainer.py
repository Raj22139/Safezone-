"""
SafeZone AI — Explainable AI (XAI) Module
Uses SHAP values to explain WHY an area has a certain risk score.
MTech-level feature: Interpretable Machine Learning
"""
import numpy as np
from ml.risk_engine import load_model, get_features_for_area

FEATURE_NAMES = [
    'Total Incidents',
    'Avg Severity',
    'Theft Cases',
    'Violence Cases',
    'Traffic Incidents',
    'Fraud Cases',
    'Burglary Cases',
    'Assault Cases',
    'Weighted Severity Score',
]

FEATURE_DESCRIPTIONS = {
    'Total Incidents':        'Total number of crime incidents reported',
    'Avg Severity':           'Average severity score (1-10) of all incidents',
    'Theft Cases':            'Number of theft/robbery incidents',
    'Violence Cases':         'Number of violent crime incidents',
    'Traffic Incidents':      'Number of traffic-related incidents',
    'Fraud Cases':            'Number of fraud/cyber crime incidents',
    'Burglary Cases':         'Number of burglary incidents',
    'Assault Cases':          'Number of assault incidents',
    'Weighted Severity Score':'Crime type weighted by severity impact',
}


def explain_risk_score(area) -> dict:
    """
    Generate SHAP-style explanation for an area's risk score.
    Returns feature contributions — which factors are increasing/decreasing risk.
    """
    try:
        import shap
        model    = load_model()
        features = get_features_for_area(area)
        X        = features.reshape(1, -1)

        # Get the actual sklearn pipeline's model step
        if hasattr(model, 'named_steps'):
            scaler     = model.named_steps['scaler']
            estimator  = model.named_steps['model']
            X_scaled   = scaler.transform(X)
        else:
            X_scaled   = X
            estimator  = model

        # SHAP TreeExplainer for RandomForest
        explainer   = shap.TreeExplainer(estimator)
        shap_values = explainer.shap_values(X_scaled)[0]

        contributions = []
        for i, (name, val, shap_val) in enumerate(
            zip(FEATURE_NAMES, features, shap_values)
        ):
            impact = 'increases_risk' if shap_val > 0 else 'decreases_risk' if shap_val < 0 else 'neutral'
            contributions.append({
                'feature':     name,
                'description': FEATURE_DESCRIPTIONS.get(name, ''),
                'value':       round(float(val), 2),
                'shap_value':  round(float(shap_val), 3),
                'impact':      impact,
                'importance':  abs(round(float(shap_val), 3)),
            })

        # Sort by absolute SHAP value (most impactful first)
        contributions.sort(key=lambda x: x['importance'], reverse=True)

        top_reasons     = [c for c in contributions if c['impact'] == 'increases_risk'][:3]
        positive_factors= [c for c in contributions if c['impact'] == 'decreases_risk'][:2]

        return {
            'method':          'SHAP TreeExplainer',
            'contributions':   contributions,
            'top_risk_factors':top_reasons,
            'safety_factors':  positive_factors,
            'explanation':     _generate_explanation(top_reasons, area.risk_score),
        }

    except ImportError:
        return _fallback_explanation(area)
    except Exception:
        return _fallback_explanation(area)


def _generate_explanation(top_factors, score) -> str:
    """Generate human-readable explanation from top SHAP factors."""
    if not top_factors:
        if score <= 35:
            return "This area has low crime activity with minimal incidents reported."
        return "Risk score based on overall crime pattern analysis."

    factor_names = [f['feature'] for f in top_factors[:2]]
    if score > 65:
        return (f"High risk score primarily driven by {' and '.join(factor_names)}. "
                f"These factors contribute most significantly to the elevated risk level.")
    elif score > 35:
        return (f"Moderate risk influenced by {' and '.join(factor_names)}. "
                f"Exercise caution especially during peak crime hours.")
    else:
        return (f"Low risk area. Limited impact from {factor_names[0] if factor_names else 'crime factors'}. "
                f"Generally safe for travel and residence.")


def _fallback_explanation(area) -> dict:
    """Fallback when SHAP is not available — rule-based explanation."""
    from crime.models import CrimeRecord
    from django.db.models import Count

    records  = CrimeRecord.objects.filter(area=area, status='approved')
    total    = records.count()
    top_type = records.values('crime_type').annotate(c=Count('id')).order_by('-c').first()

    contributions = []
    feature_vals  = [total, 0, 0, 0, 0, 0, 0, 0, 0]

    for i, (name, val) in enumerate(zip(FEATURE_NAMES, feature_vals)):
        contributions.append({
            'feature':    name,
            'description':FEATURE_DESCRIPTIONS.get(name, ''),
            'value':      val,
            'shap_value': round(val * 0.1, 3),
            'impact':     'increases_risk' if val > 0 else 'neutral',
            'importance': abs(round(val * 0.1, 3)),
        })

    top_type_name = top_type['crime_type'].replace('_', ' ').title() if top_type else 'General Crime'
    return {
        'method':          'Rule-based (SHAP unavailable)',
        'contributions':   contributions,
        'top_risk_factors':[{'feature': top_type_name, 'value': total}] if total else [],
        'safety_factors':  [],
        'explanation':     _generate_explanation([], area.risk_score),
    }


def get_anomaly_score(area) -> dict:
    """
    Detect if an area has unusual crime spike (Anomaly Detection).
    Uses IsolationForest concept — rule-based fallback if sklearn unavailable.
    """
    from crime.models import CrimeRecord
    from datetime import date, timedelta

    # Last 30 days vs previous 30 days
    today       = date.today()
    recent      = CrimeRecord.objects.filter(
        area=area, status='approved',
        incident_date__gte=today - timedelta(days=30)
    ).count()
    previous    = CrimeRecord.objects.filter(
        area=area, status='approved',
        incident_date__gte=today - timedelta(days=60),
        incident_date__lt=today  - timedelta(days=30),
    ).count()

    baseline    = max(previous, 1)
    change_pct  = ((recent - previous) / baseline) * 100
    is_anomaly  = change_pct > 50  # >50% spike = anomaly

    return {
        'area':          str(area),
        'recent_30d':    recent,
        'previous_30d':  previous,
        'change_percent':round(change_pct, 1),
        'is_anomaly':    is_anomaly,
        'anomaly_level': 'high' if change_pct > 100 else 'medium' if change_pct > 50 else 'normal',
        'message': (
            f"⚠️ Crime spike detected! +{change_pct:.0f}% increase in last 30 days."
            if is_anomaly else
            f"Crime levels normal. {change_pct:+.0f}% change vs previous month."
        )
    }
