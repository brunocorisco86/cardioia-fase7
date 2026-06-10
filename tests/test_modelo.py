import numpy as np
import pandas as pd
from modelo import ModeloRiscoColisao

def test_modelo_inicializacao():
    modelo = ModeloRiscoColisao(seed=10)
    assert modelo.metricas == {}
    assert modelo.rede is not None
    assert modelo.scaler is not None

def test_modelo_treinamento(eventos_simulados):
    modelo = ModeloRiscoColisao(seed=42)
    metricas = modelo.treinar(eventos_simulados)
    
    assert isinstance(metricas, dict)
    chaves_esperadas = {
        "acuracia", "precisao", "recall", "f1", 
        "auc_roc", "matriz_confusao", "n_treino", "n_teste"
    }
    assert chaves_esperadas.issubset(metricas.keys())
    
    # Valida faixas aceitáveis das métricas de desempenho
    for key in ["acuracia", "precisao", "recall", "f1", "auc_roc"]:
        assert 0.0 <= metricas[key] <= 1.0
        
    assert metricas["n_treino"] > 0
    assert metricas["n_teste"] > 0
    assert len(metricas["matriz_confusao"]) == 2
    assert len(metricas["matriz_confusao"][0]) == 2

def test_modelo_previsao(modelo_treinado, eventos_simulados):
    predicoes = modelo_treinado.prever_risco(eventos_simulados)
    
    assert isinstance(predicoes, np.ndarray)
    assert len(predicoes) == len(eventos_simulados)
    
    # Todas as probabilidades previstas devem estar no intervalo [0, 1]
    assert np.all(predicoes >= 0.0)
    assert np.all(predicoes <= 1.0)
