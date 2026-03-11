import pandas as pd
from sklearn.metrics import roc_auc_score

TEST_LABELS_FILE = "data/hidden_test_labels.csv"


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

    test = pd.read_csv(TEST_LABELS_FILE)

    if "id" not in test.columns or "label" not in test.columns:
        raise Exception("hidden_test_labels.csv must contain columns: id,label")

    test["label"] = pd.to_numeric(test["label"], errors="coerce")

    if test["label"].isnull().any():
        raise Exception("Test labels contain invalid values")

    test["label"] = test["label"].astype(int)

    if not test["label"].isin([0, 1]).all():
        raise Exception("Test labels must be 0 or 1")

    if len(df) != len(test):
        raise Exception("Submission length does not match test set")

    df = df.sort_values("id").reset_index(drop=True)
    test = test.sort_values("id").reset_index(drop=True)

    if not (df["id"].astype(str).values == test["id"].astype(str).values).all():
        raise Exception("IDs do not match test set")

    if test["label"].nunique() < 2:
        raise Exception("ROC-AUC requires both classes 0 and 1 in hidden_test_labels.csv")

    score = roc_auc_score(test["label"], df["prediction"])
    return score