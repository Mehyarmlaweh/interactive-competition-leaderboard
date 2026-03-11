import pandas as pd
import io
import streamlit as st
from sklearn.metrics import roc_auc_score


def _load_test_labels():
    """Load hidden test labels from Streamlit secrets."""
    try:
        raw = st.secrets["TEST_LABELS"]
    except KeyError:
        raise Exception(
            "TEST_LABELS not found in secrets. "
            "Add it under Settings → Secrets in Streamlit Cloud, "
            "or in .streamlit/secrets.toml for local development."
        )
    test = pd.read_csv(io.StringIO(raw))
    return test


def evaluate_submission(file):
    df = pd.read_csv(file)

    if "id" not in df.columns or "prediction" not in df.columns:
        raise Exception("CSV must contain columns: id,prediction")

    df["prediction"] = pd.to_numeric(df["prediction"], errors="coerce")

    if df["prediction"].isnull().any():
        raise Exception("Prediction column contains invalid or missing values")

    if not ((df["prediction"] >= 0) & (df["prediction"] <= 1)).all():
        raise Exception("Predictions must be probabilities between 0 and 1")

    if df["id"].duplicated().any():
        raise Exception("Duplicate IDs found in submission")

    test = _load_test_labels()

    if "id" not in test.columns or "label" not in test.columns:
        raise Exception("TEST_LABELS secret must contain columns: id,label")

    test["label"] = pd.to_numeric(test["label"], errors="coerce")

    if test["label"].isnull().any():
        raise Exception("Test labels contain invalid values")

    test["label"] = test["label"].astype(int)

    if not test["label"].isin([0, 1]).all():
        raise Exception("Test labels must be 0 or 1")

    if len(df) != len(test):
        raise Exception(f"Submission has {len(df)} rows but test set expects {len(test)}")

    df = df.sort_values("id").reset_index(drop=True)
    test = test.sort_values("id").reset_index(drop=True)

    if not (df["id"].astype(str).values == test["id"].astype(str).values).all():
        raise Exception("IDs do not match the test set")

    if test["label"].nunique() < 2:
        raise Exception("Test labels must contain both classes 0 and 1")

    score = roc_auc_score(test["label"], df["prediction"])
    return score