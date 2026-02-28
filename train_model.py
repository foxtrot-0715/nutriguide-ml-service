import pandas as pd
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge  # Более легкий алгоритм
from sklearn.pipeline import Pipeline
from sklearn.multioutput import MultiOutputRegressor

def train():
    csv_path = 'food_data.csv'
    model_save_path = 'app/models/food_model.joblib'

    df = pd.read_csv(csv_path)
    # Очистка названий колонок (убираем пробелы)
    df.columns = [c.strip() for c in df.columns]

    X = df['food'].astype(str).str.lower()
    y = df[['p', 'f', 'c', 'kcal']].apply(pd.to_numeric, errors='coerce').fillna(0)

    print("🧠 Обучаю ML-модель (Ridge Regression)...")
    
    # Используем Ridge — это честный ML с регуляризацией
    model = Pipeline([
        ('vectorizer', TfidfVectorizer(ngram_range=(1, 2))),
        ('regressor', MultiOutputRegressor(Ridge()))
    ])

    model.fit(X, y)
    
    os.makedirs('app/models', exist_ok=True)
    joblib.dump(model, model_save_path)
    print(f"✅ Модель сохранена: {model_save_path}")

if __name__ == "__main__":
    train()
