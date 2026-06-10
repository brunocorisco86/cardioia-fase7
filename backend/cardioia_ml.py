import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib

# 1. Geração da Base de Dados Sintética
def generate_synthetic_data(n_samples=1000):
    np.random.seed(42)
    data = {
        'idade': np.random.randint(20, 90, n_samples),
        'frequencia_cardiaca': np.random.randint(50, 120, n_samples),
        'spo2': np.random.randint(85, 100, n_samples),
        'carga_sistema': np.random.uniform(0.1, 1.0, n_samples),
        'disponibilidade_recursos': np.random.uniform(0.1, 1.0, n_samples),
        'historico_cardiaco': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    }
    
    df = pd.DataFrame(data)
    
    # Lógica para definir o pico_risco (variável alvo)
    # Risco aumenta com idade, frequência cardíaca alta, spo2 baixo e carga do sistema alta
    score = (
        (df['idade'] / 90) * 0.2 +
        (df['frequencia_cardiaca'] / 120) * 0.3 +
        ((100 - df['spo2']) / 15) * 0.3 +
        (df['carga_sistema']) * 0.1 +
        (df['historico_cardiaco']) * 0.1
    )
    
    df['pico_risco'] = (score > 0.6).astype(int)
    return df

# 2. Treinamento do Modelo
def train_model(df):
    X = df.drop('pico_risco', axis=1)
    y = df['pico_risco']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        'report': classification_report(y_test, y_pred, output_dict=True)
    }
    
    return model, metrics, X_test, y_test

if __name__ == "__main__":
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    df = generate_synthetic_data()
    csv_path = os.path.join(BASE_DIR, 'base_cardioia.csv')
    df.to_csv(csv_path, index=False)
    print(f"Base de dados gerada e salva em '{csv_path}'.")
    
    model, metrics, X_test, y_test = train_model(df)
    model_path = os.path.join(BASE_DIR, 'modelo_cardioia.pkl')
    joblib.dump(model, model_path)
    print(f"Modelo treinado e salvo em '{model_path}'.")
    
    print(f"Acurácia: {metrics['accuracy']:.4f}")
    print("Matriz de Confusão:")
    print(np.array(metrics['confusion_matrix']))
