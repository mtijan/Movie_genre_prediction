import os
import pickle

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC

# gunakan local mlruns (hindari error sqlite)
mlflow.set_tracking_uri("file:./mlruns")

# pastikan folder models/ ada
os.makedirs("models", exist_ok=True)


def load_data(path):
    return pd.read_csv(path)


def train():
    df = load_data("data/movies.csv")

    # Filter ke genre utama yang punya cukup data
    MAIN_GENRES = ["Action", "Comedy", "Drama", "Horror", "Thriller"]
    df = df[df["genre"].isin(MAIN_GENRES)].reset_index(drop=True)
    print(f"Dataset setelah filter genre: {len(df)} baris")
    print(f"Genre distribution:\n{df['genre'].value_counts()}\n")

    X = df["overview"]
    y = df["genre"]

    # split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # vectorizer (fit hanya di train)
    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),     # unigram + bigram
        sublinear_tf=True,      # normalisasi TF
        min_df=2,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = LinearSVC(max_iter=2000, C=5.0, dual="auto")

    with mlflow.start_run():
        # training
        model.fit(X_train_vec, y_train)

        # prediction
        y_pred = model.predict(X_test_vec)

        # metrics
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)

        # log params
        mlflow.log_param("model", "LinearSVC")
        mlflow.log_param("max_features", 10000)
        mlflow.log_param("ngram_range", "(1,2)")
        mlflow.log_param("sublinear_tf", True)
        mlflow.log_param("test_size", 0.2)
        mlflow.log_param("C", 5.0)

        # log metrics
        mlflow.log_metric("accuracy", accuracy)

        # log model ke MLflow
        mlflow.sklearn.log_model(model, "model")

        # simpan vectorizer ke root (untuk MLflow artifact) & models/
        pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))
        pickle.dump(vectorizer, open("models/vectorizer.pkl", "wb"))
        mlflow.log_artifact("vectorizer.pkl")

        # simpan model lokal ke models/model.pkl (dipakai FastAPI)
        pickle.dump(model, open("models/model.pkl", "wb"))

        # simpan classification report ke artifact
        with open("models/classification_report.txt", "w") as f:
            f.write(report)
        mlflow.log_artifact("models/classification_report.txt")

        print("=" * 50)
        print("Training selesai!")
        print(f"Model    : LinearSVC")
        print(f"Accuracy : {accuracy:.4f}")
        print("=" * 50)
        print("\nClassification Report:")
        print(report)
        print("\nModel disimpan ke: models/model.pkl")
        print("Vectorizer disimpan ke: models/vectorizer.pkl")


if __name__ == "__main__":
    train()