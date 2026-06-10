import os
from unittest.mock import patch
from genai import gerar_briefing

def test_gerar_briefing_offline():
    # Dados de entrada simulados
    metricas = {
        "acuracia": 0.95,
        "f1": 0.88,
        "auc_roc": 0.99
    }
    recomendacoes = [
        {
            "primario": "OBJ-00001",
            "secundario": "OBJ-00002",
            "risco": 0.89,
            "distancia_minima_km": 1.20,
            "tempo_ate_aprox_h": 12.0,
            "acao_recomendada": "MANOBRA EVASIVA IMEDIATA"
        }
    ]
    visao = {
        "objetos_reais": 10,
        "objetos_detectados": 8
    }
    
    # Executa com garantia de que a chave API não está definida (teste offline)
    with patch.dict(os.environ, {}, clear=True):
        briefing = gerar_briefing(metricas, recomendacoes, visao)
        
    assert isinstance(briefing, str)
    assert "BRIEFING OPERACIONAL" in briefing
    assert "DESEMPENHO DO MODELO DE RISCO" in briefing
    assert "VISÃO COMPUTACIONAL" in briefing
    assert "SITUAÇÃO DE RISCO" in briefing
    assert "OBJ-00001 x OBJ-00002" in briefing
    assert "MANOBRA EVASIVA IMEDIATA" in briefing

def test_gerar_briefing_fallback_erro():
    metricas = {"acuracia": 0.9, "f1": 0.8, "auc_roc": 0.9}
    recomendacoes = []
    visao = {"objetos_reais": 5, "objetos_detectados": 5}
    
    # Simula que a chave API está definida, mas a chamada falha catastroficamente
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"}):
        briefing = gerar_briefing(metricas, recomendacoes, visao)
        
    # Deve fazer o fallback para o template e exibir a mensagem de aviso da falha
    assert isinstance(briefing, str)
    assert "BRIEFING OPERACIONAL" in briefing
    assert "chamada à API falhou" in briefing
