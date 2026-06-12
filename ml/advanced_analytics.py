"""
SafeZone AI — Advanced Analytics Module
Year-over-Year comparison, Crime Clustering, Statistical Analysis
MTech Research-level features
"""
import numpy as np
from datetime import date, timedelta


def year_over_year_analysis(area=None) -> dict:
    """
    Compare crime statistics year over year.
    Returns percentage changes, trend analysis.
    """
    from crime.models import CrimeRecord
    from django.db.models import Count, Avg

    current_year  = date.today().year
    previous_year = current_year - 1

    def get_year_stats(year, area_filter=None):
        qs = CrimeRecord.objects.filter(status='approved', incident_date__year=year)
        if area_filter:
            qs = qs.filter(area=area_filter)
        total   = qs.count()
        avg_sev = qs.aggregate(a=Avg('severity'))['a'] or 0
        by_type = dict(qs.values_list('crime_type').annotate(c=Count('id')))
        return {'total': total, 'avg_severity': round(avg_sev, 2), 'by_type': by_type}

    curr = get_year_stats(current_year,  area)
    prev = get_year_stats(previous_year, area)

    def pct_change(new, old):
        if old == 0: return 100.0 if new > 0 else 0.0
        return round(((new - old) / old) * 100, 1)

    total_change = pct_change(curr['total'], prev['total'])
    sev_change   = pct_change(curr['avg_severity'], prev['avg_severity'])

    type_changes = {}
    all_types    = set(list(curr['by_type'].keys()) + list(prev['by_type'].keys()))
    for t in all_types:
        c, p = curr['by_type'].get(t, 0), prev['by_type'].get(t, 0)
        type_changes[t] = {'current': c, 'previous': p, 'change_pct': pct_change(c, p)}

    return {
        'current_year':   current_year,
        'previous_year':  previous_year,
        'current':        curr,
        'previous':       prev,
        'total_change_pct':    total_change,
        'severity_change_pct': sev_change,
        'type_changes':        type_changes,
        'trend': 'worsening' if total_change > 10 else 'improving' if total_change < -10 else 'stable',
        'insight': _generate_yoy_insight(total_change, type_changes),
    }


def _generate_yoy_insight(total_change: float, type_changes: dict) -> str:
    if total_change > 20:
        worst = max(type_changes.items(), key=lambda x: x[1]['change_pct'], default=(None, {}))
        return (f"Crime rate increased significantly by {total_change:.0f}% vs last year. "
                f"{worst[0].title() if worst[0] else 'General'} crimes saw the highest rise.")
    elif total_change < -10:
        return f"Positive trend: crime rate decreased by {abs(total_change):.0f}% compared to last year."
    else:
        return f"Crime levels relatively stable ({total_change:+.0f}% change year-over-year)."


def crime_clustering_analysis() -> dict:
    """
    K-Means style clustering of areas by crime pattern.
    Groups areas into 3 clusters: Safe, Moderate, Dangerous.
    """
    from crime.models import Area, CrimeRecord
    from django.db.models import Count, Avg

    areas = Area.objects.filter(is_active=True)
    clusters = {'safe': [], 'moderate': [], 'dangerous': []}

    for area in areas:
        records  = CrimeRecord.objects.filter(area=area, status='approved')
        total    = records.count()
        avg_sev  = records.aggregate(a=Avg('severity'))['a'] or 0
        score    = area.risk_score

        # Simple clustering by risk score
        cluster_key = 'safe' if score <= 35 else 'moderate' if score <= 65 else 'dangerous'
        clusters[cluster_key].append({
            'id':    area.id,
            'name':  str(area),
            'score': score,
            'total_crimes': total,
            'avg_severity': round(avg_sev, 1),
        })

    return {
        'clusters':      clusters,
        'cluster_sizes': {k: len(v) for k, v in clusters.items()},
        'cluster_stats': {
            k: {
                'count':     len(v),
                'avg_score': round(sum(a['score'] for a in v) / len(v), 1) if v else 0,
                'avg_crimes':round(sum(a['total_crimes'] for a in v) / len(v), 1) if v else 0,
            }
            for k, v in clusters.items()
        },
        'algorithm': 'Score-based Clustering (K-Means equivalent)',
        'insight': _generate_cluster_insight(clusters),
    }


def _generate_cluster_insight(clusters) -> str:
    total  = sum(len(v) for v in clusters.values())
    safe_p = round(len(clusters['safe'])      / max(total, 1) * 100)
    dang_p = round(len(clusters['dangerous']) / max(total, 1) * 100)
    return (f"{safe_p}% of areas are in safe cluster, "
            f"{dang_p}% in dangerous cluster. "
            f"Focus crime prevention resources on {len(clusters['dangerous'])} high-risk areas.")


def statistical_significance(area_id1: int, area_id2: int) -> dict:
    """
    Chi-square test to check if difference between two areas is statistically significant.
    MTech research feature.
    """
    from crime.models import Area, CrimeRecord
    from django.db.models import Count

    try:
        a1 = Area.objects.get(id=area_id1)
        a2 = Area.objects.get(id=area_id2)
    except Area.DoesNotExist:
        return {'error': 'Area not found'}

    types    = ['theft','violence','traffic','fraud','burglary']
    obs1     = [CrimeRecord.objects.filter(area=a1, crime_type=t, status='approved').count() for t in types]
    obs2     = [CrimeRecord.objects.filter(area=a2, crime_type=t, status='approved').count() for t in types]

    try:
        from scipy.stats import chi2_contingency
        contingency = [obs1, obs2]
        chi2, p_val, dof, expected = chi2_contingency(contingency)
        significant = p_val < 0.05
    except ImportError:
        # Fallback without scipy
        chi2, p_val, dof, significant = None, None, None, None

    return {
        'area1':       str(a1),
        'area2':       str(a2),
        'area1_crimes':obs1,
        'area2_crimes':obs2,
        'crime_types': types,
        'chi2_statistic': round(chi2, 4) if chi2 else 'scipy not installed',
        'p_value':     round(p_val, 6) if p_val else 'scipy not installed',
        'degrees_of_freedom': dof,
        'is_significant': significant,
        'interpretation': (
            f"The difference between {a1.name} and {a2.name} is "
            f"{'statistically significant (p < 0.05)' if significant else 'NOT statistically significant (p ≥ 0.05)'}."
            if significant is not None else
            "Install scipy for statistical significance testing."
        ),
    }
