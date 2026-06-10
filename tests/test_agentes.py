import pytest
import pandas as pd
from agentes import (Mensagem, Barramento, AgenteMonitor, AgenteAnalista,
                     AgenteDecisor, orquestrar)

def test_barramento_e_mensagens():
    barramento = Barramento()
    assert len(barramento.historico) == 0
    
    msg = Mensagem(remetente="Teste", tipo="info", conteudo="Olá mundo")
    barramento.publicar(msg)
    
    assert len(barramento.historico) == 1
    assert barramento.log() == ["[Teste] info"]

def test_agente_monitor(eventos_simulados):
    barramento = Barramento()
    monitor = AgenteMonitor()
    
    res = monitor.perceber(eventos_simulados, barramento)
    
    assert res is eventos_simulados
    assert len(barramento.historico) == 1
    assert barramento.historico[0].remetente == "AgenteMonitor"
    assert barramento.historico[0].tipo == "ingestao"

def test_agente_analista(modelo_treinado, eventos_simulados):
    barramento = Barramento()
    analista = AgenteAnalista(modelo_treinado)
    
    res_df = analista.analisar(eventos_simulados, barramento)
    
    assert "risco_previsto" in res_df.columns
    assert len(barramento.historico) == 1
    assert barramento.historico[0].remetente == "AgenteAnalista"
    assert barramento.historico[0].tipo == "analise"

def test_agente_decisor(modelo_treinado, eventos_simulados):
    barramento = Barramento()
    analista = AgenteAnalista(modelo_treinado)
    decisor = AgenteDecisor()
    
    # Prepara eventos com coluna risco_previsto
    eventos_analisados = analista.analisar(eventos_simulados, barramento)
    
    recoms = decisor.decidir(eventos_analisados, barramento, top_n=3)
    
    assert isinstance(recoms, list)
    assert len(recoms) == 3
    assert len(barramento.historico) == 2  # 1 do analista + 1 do decisor
    
    # Verifica estrutura da recomendação
    chaves = {"primario", "secundario", "risco", "distancia_minima_km", "tempo_ate_aprox_h", "acao_recomendada"}
    for rec in recoms:
        assert chaves.issubset(rec.keys())
        
    # As recomendações devem ser ordenadas por risco decrescente
    riscos = [r["risco"] for r in recoms]
    assert riscos == sorted(riscos, reverse=True)

def test_orquestrar_sistema_multiagente(modelo_treinado, eventos_simulados):
    recoms, barramento, eventos_final = orquestrar(eventos_simulados, modelo_treinado)
    
    assert isinstance(recoms, list)
    assert len(recoms) > 0
    assert len(barramento.historico) == 3  # Monitor, Analista, Decisor publicaram
    assert "risco_previsto" in eventos_final.columns
