import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import cross_val_score
import joblib
import os
from core.ml.preprocessor import preprocess_text

def train_model(training_csv: str, model_out: str, vectorizer_out: str):
    if not os.path.exists(training_csv):
        print(f"Training data not found at {training_csv}")
        return

    df = pd.read_csv(training_csv)
    
    if df.empty or "description" not in df.columns or "category" not in df.columns:
        print("Invalid training data format.")
        return

    # Preprocess
    df["description_clean"] = df["description"].apply(preprocess_text)
    
    # Filter out empty descriptions after cleaning
    df = df[df["description_clean"].str.strip() != ""]

    # Build pipeline
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X = vectorizer.fit_transform(df["description_clean"])
    y = df["category"]

    # Train
    model = MultinomialNB(alpha=0.1)
    model.fit(X, y)

    # Evaluate (only if we have enough samples per class for cross-validation)
    try:
        scores = cross_val_score(model, X, y, cv=3, scoring="accuracy")
        print(f"Cross-val accuracy: {scores.mean():.3f} +- {scores.std():.3f}")
    except Exception as e:
        print(f"Skipping cross-validation due to data distribution: {e}")

    # Ensure output directories exist
    os.makedirs(os.path.dirname(model_out), exist_ok=True)

    # Save artifacts
    joblib.dump(model, model_out)
    joblib.dump(vectorizer, vectorizer_out)
    print("Model and vectorizer saved successfully.")

if __name__ == "__main__":
    train_model(
        "data/training/transactions.csv",
        "ml_models/category_classifier.pkl",
        "ml_models/tfidf_vectorizer.pkl"
    )
