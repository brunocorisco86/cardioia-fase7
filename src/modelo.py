"""
Módulo de Modelo — ORBITAL-IA
==============================
Rede neural (Multi-Layer Perceptron) que aprende a prever o risco de
colisão entre objetos orbitais a partir das features de conjunção.

Usa scikit-learn (MLPClassifier) para garantir execução leve e reprodutível.
A arquitetura e o pré-processamento são facilmente portáveis para PyTorch/
TensorFlow caso a equipe queira escalar o treinamento (ver README, item
"Próximos passos").
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix)

FEATURES = [
    "distancia_minima_km",
    "velocidade_relativa_kms",
    "tamanho_combinado_m",
    "diferenca_altitude_km",
    "tempo_ate_aprox_h",
]


class ModeloRiscoColisao:
    """Rede neural para classificação de risco de colisão orbital."""

    def __init__(self, seed: int = 42):
        self.scaler = StandardScaler()
        self.rede = MLPClassifier(
            hidden_layer_sizes=(32, 16),
            activation="relu",
            solver="adam",
            alpha=1e-4,
            max_iter=400,
            random_state=seed,
        )
        self.metricas: dict = {}

    def treinar(self, eventos: pd.DataFrame) -> dict:
        X = eventos[FEATURES].values
        y = eventos["risco_real"].values
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y)

        X_tr = self.scaler.fit_transform(X_tr)
        X_te = self.scaler.transform(X_te)
        self.rede.fit(X_tr, y_tr)

        y_pred = self.rede.predict(X_te)
        y_proba = self.rede.predict_proba(X_te)[:, 1]

        self.metricas = {
            "acuracia": round(accuracy_score(y_te, y_pred), 4),
            "precisao": round(precision_score(y_te, y_pred, zero_division=0), 4),
            "recall": round(recall_score(y_te, y_pred, zero_division=0), 4),
            "f1": round(f1_score(y_te, y_pred, zero_division=0), 4),
            "auc_roc": round(roc_auc_score(y_te, y_proba), 4),
            "matriz_confusao": confusion_matrix(y_te, y_pred).tolist(),
            "n_treino": int(len(X_tr)),
            "n_teste": int(len(X_te)),
        }
        return self.metricas

    def prever_risco(self, eventos: pd.DataFrame) -> np.ndarray:
        """Retorna a probabilidade de risco (0 a 1) para cada evento."""
        X = self.scaler.transform(eventos[FEATURES].values)
        return self.rede.predict_proba(X)[:, 1]


if __name__ == "__main__":
    from dados import gerar_catalogo, gerar_eventos_conjuncao
    cat = gerar_catalogo()
    ev = gerar_eventos_conjuncao(cat)
    modelo = ModeloRiscoColisao()
    print(modelo.treinar(ev))
