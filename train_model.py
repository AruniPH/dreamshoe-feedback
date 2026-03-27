"""
Train and save the feedback classification model.
Dataset columns: Product, Feature, SubFeature, Feedback, ImprovementNeeded
Label: Yes -> 1 (Need Improvement), No -> 0 (No Need Improvement)
"""

import os
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report

# ── Paths ──────────────────────────────────────────────────────────────────────
DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "footwear_feedback_dataset_labeled.csv")
MODELS_DIR   = os.path.join(os.path.dirname(__file__), "models")

# ── Load & deduplicate conflicting labels ──────────────────────────────────────
df = pd.read_csv(DATASET_PATH)
df.columns = df.columns.str.strip()
df["text"]  = df["Feature"] + " " + df["SubFeature"] + " " + df["Feedback"]
df["label"] = (df["ImprovementNeeded"].str.strip().str.lower() == "yes").astype(int)

# For rows with same text but conflicting labels, keep majority vote
df = (df.groupby("text")["label"]
        .agg(lambda x: int(x.mean() >= 0.5))
        .reset_index())

X = df["text"].values
y = df["label"].values
print(f"Dataset size after deduplication: {len(df)} rows")
print(f"Label distribution: {dict(df['label'].value_counts())}\n")

# ── Compare classifiers ────────────────────────────────────────────────────────
tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=5000, sublinear_tf=True)
cv    = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

candidates = {
    "Logistic Regression": LogisticRegression(C=1.0, max_iter=1000, random_state=42),
    "LinearSVC":           LinearSVC(C=1.0, max_iter=2000, random_state=42),
    "Random Forest":       RandomForestClassifier(n_estimators=200, random_state=42),
    "Gradient Boosting":   GradientBoostingClassifier(n_estimators=200, random_state=42),
}

best_score, best_name, best_clf = 0, None, None
for name, clf in candidates.items():
    pipe   = Pipeline([("tfidf", tfidf), ("clf", clf)])
    scores = cross_val_score(pipe, X, y, cv=cv, scoring="accuracy")
    print(f"{name:25s}  CV accuracy: {scores.mean():.4f} ± {scores.std():.4f}")
    if scores.mean() > best_score:
        best_score, best_name, best_clf = scores.mean(), name, clf

print(f"\nBest model: {best_name} ({best_score:.4f})")

# ── Train best model on full dataset ──────────────────────────────────────────
best_pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000, sublinear_tf=True)),
    ("clf",   best_clf),
])
best_pipeline.fit(X, y)
y_pred = best_pipeline.predict(X)
print("\nClassification Report (full training data):")
print(classification_report(y, y_pred, target_names=["No Need Improvement", "Need Improvement"]))

# ── Save ───────────────────────────────────────────────────────────────────────
os.makedirs(MODELS_DIR, exist_ok=True)
joblib.dump(best_pipeline.named_steps["clf"],   os.path.join(MODELS_DIR, "model.pkl"))
joblib.dump(best_pipeline.named_steps["tfidf"], os.path.join(MODELS_DIR, "vectorizer.pkl"))
print(f"Saved model.pkl and vectorizer.pkl to: {MODELS_DIR}")
