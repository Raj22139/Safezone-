"""
SafeZone AI — ML Risk Scoring Engine
Uses Scikit-learn to train and predict area risk scores.
"""

import os
import numpy as np
import joblib
from pathlib import Path
from django.conf import settings
from django.db.models import Avg


# ── Feature weights used for synthetic training ──
CRIME_WEIGHTS = {
    'theft':     0.25,
    'violence':  0.30,
    'traffic':   0.15,
    'fraud':     0.15,
    'burglary':  0.10,
    'assault':   0.30,
    'vandalism': 0.08,
    'other':     0.05,
}

MODEL_PATH = Path(settings.BASE_DIR) / 'ml' / 'trained_model' / 'risk_model.pkl'


def get_features_for_area(area):
    """
    Build a feature vector for an Area object from its CrimeRecords.
    Features:
      [0]  total_incidents
      [1]  avg_severity
      [2]  theft_count
      [3]  violence_count
      [4]  traffic_count
      [5]  fraud_count
      [6]  burglary_count
      [7]  assault_count
      [8]  weighted_severity_score
    """
    from crime.models import CrimeRecord

    records = CrimeRecord.objects.filter(area=area, status='approved')

    if not records.exists():
        return np.zeros(9)

    total       = records.count()
    avg_sev     = records.aggregate(avg=Avg('severity'))['avg'] or 0

    counts = {k: 0 for k in CRIME_WEIGHTS}
    weighted = 0.0

    for r in records:
        ctype = r.crime_type
        if ctype in counts:
            counts[ctype] += 1
        weighted += r.severity * CRIME_WEIGHTS.get(ctype, 0.05)

    return np.array([
        total,
        avg_sev,
        counts['theft'],
        counts['violence'],
        counts['traffic'],
        counts['fraud'],
        counts['burglary'],
        counts['assault'],
        weighted,
    ], dtype=float)


def train_and_save_model():
    """
    Train a RandomForest regression model on synthetic data
    and save it to disk. Call this once (or via management command).
    """
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline

    np.random.seed(42)
    n = 2000

    # Synthetic feature matrix
    total       = np.random.randint(0, 80,  n).astype(float)
    avg_sev     = np.random.uniform(1, 10,  n)
    theft       = np.random.randint(0, 30,  n).astype(float)
    violence    = np.random.randint(0, 20,  n).astype(float)
    traffic     = np.random.randint(0, 40,  n).astype(float)
    fraud       = np.random.randint(0, 15,  n).astype(float)
    burglary    = np.random.randint(0, 10,  n).astype(float)
    assault     = np.random.randint(0, 10,  n).astype(float)
    weighted    = (
        theft    * 0.25 +
        violence * 0.30 +
        traffic  * 0.15 +
        fraud    * 0.15 +
        burglary * 0.10 +
        assault  * 0.30
    ) * avg_sev / 10.0

    X = np.column_stack([total, avg_sev, theft, violence, traffic, fraud, burglary, assault, weighted])

    # Target: risk score 0-100
    y = np.clip(
        (total * 0.4 + weighted * 1.5 + avg_sev * 2.0) * 1.2 + np.random.normal(0, 3, n),
        0, 100
    )

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model',  RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)),
    ])

    pipeline.fit(X_train, y_train)

    # Save model
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    score = pipeline.score(X_test, y_test)
    print(f"[ML] Model trained. R² score: {score:.4f}. Saved to {MODEL_PATH}")
    return pipeline


def load_model():
    """Load saved model, or train fresh if not found."""
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    print("[ML] Model not found — training now...")
    return train_and_save_model()


def predict_risk_score(features: np.ndarray) -> int:
    """
    Given a feature vector, return an integer risk score 0-100.
    """
    model = load_model()
    score = model.predict(features.reshape(1, -1))[0]
    return int(np.clip(round(score), 0, 100))


def predict_risk_for_area(area) -> dict:
    """
    Full prediction pipeline for an Area instance.
    Returns dict with score, level, and description.
    """
    features = get_features_for_area(area)
    score    = predict_risk_score(features)

    if score <= 35:
        level = 'low'
        desc  = "This area has low crime activity. Generally safe for residence and travel."
    elif score <= 65:
        level = 'medium'
        desc  = "Moderate crime activity detected. Stay alert, especially during night hours."
    else:
        level = 'high'
        desc  = "High crime activity detected. Significant risk — take precautions and consider safer alternatives."

    return {
        'score': score,
        'level': level,
        'description': desc,
        'features': features.tolist(),
        'crime_counts': {
            'theft':    int(features[2]),
            'violence': int(features[3]),
            'traffic':  int(features[4]),
            'fraud':    int(features[5]),
            'burglary': int(features[6]),
            'assault':  int(features[7]),
        }
    }


def get_safer_areas(area, limit=3):
    """
    Return nearby safer areas (same city, lower risk score).
    """
    from crime.models import Area as AreaModel

    safer = AreaModel.objects.filter(
        city=area.city,
        risk_level='low',
        is_active=True,
    ).exclude(id=area.id).order_by('risk_score')[:limit]

    if safer.count() < limit:
        # Include medium risk if not enough low-risk areas
        medium = AreaModel.objects.filter(
            city=area.city,
            risk_level='medium',
            is_active=True,
        ).exclude(id=area.id).order_by('risk_score')[:limit - safer.count()]
        return list(safer) + list(medium)

    return list(safer)
