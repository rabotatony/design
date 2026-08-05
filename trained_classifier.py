"""trained_classifier.py — feature-based AI image classifier using sklearn.

Extracts hand-crafted features (frequency, noise, saturation) and trains a
sklearn classifier to distinguish real vs AI images. This is the path to
reliable photorealistic detection (the statistical heuristics have a ceiling).

Requires a labeled dataset (real vs AI images) to train. The more data, the
better. This is the honest path to truly good photorealistic detection.
"""
import os
import numpy as np
from PIL import Image

try:
    from feature_extractor import extract_features
except ImportError:
    extract_features = None

FEATURE_KEYS = ["high_freq_ratio", "noise_std", "noise_corr", "saturation_mean", "saturation_std"]


def featurize_dir(dir_path, label):
    """Extract features from all images in a directory. Returns (X, y)."""
    X, y = [], []
    for f in sorted(os.listdir(dir_path)):
        if not f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            continue
        p = os.path.join(dir_path, f)
        try:
            feats = extract_features(p)
            X.append([feats[k] for k in FEATURE_KEYS])
            y.append(label)
        except Exception as e:
            print(f"  skip {f}: {e}")
    return X, y


def train_classifier(real_dir, ai_dir):
    """Train a classifier on real vs AI image directories."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score
    Xr, yr = featurize_dir(real_dir, 0)
    Xa, ya = featurize_dir(ai_dir, 1)
    X = np.array(Xr + Xa)
    y = np.array(yr + ya)
    if len(X) < 10:
        return None, {"error": f"need more data: {len(X)} images"}
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    scores = cross_val_score(clf, X, y, cv=min(5, len(X)//2), scoring="accuracy")
    clf.fit(X, y)
    return clf, {"n_images": len(X), "cv_accuracy_mean": float(scores.mean()),
                 "cv_accuracy_std": float(scores.std())}


def classify_image(clf, image_path):
    feats = extract_features(image_path)
    X = np.array([[feats[k] for k in FEATURE_KEYS]])
    prob = clf.predict_proba(X)[0]
    return {"ai_probability": float(prob[1]), "verdict": "ai_likely" if prob[1] > 0.5 else "human_likely"}
