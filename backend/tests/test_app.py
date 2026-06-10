import os
import sys
import pytest
from fastapi.testclient import TestClient

# Adiciona o diretório backend ao path para permitir a importação de app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(BASE_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from app import app

client = TestClient(app)

def test_read_root():
    """Valida a rota de health check inicial da API."""
    response = client.get("/")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "online"
    assert json_data["service"] == "CardioIA API"

def test_update_telemetry_normal():
    """Valida o envio de telemetria com sinais vitais dentro dos limites normais."""
    payload = {
        "temperatura": 36.5,
        "frequencia_cardiaca": 80
    }
    response = client.post("/api/telemetry", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert json_data["telemetry"]["temperatura"] == 36.5
    assert json_data["telemetry"]["frequencia_cardiaca"] == 80
    assert json_data["telemetry"]["alerta"] is False
    assert "normais" in json_data["telemetry"]["mensagem_alerta"]

def test_update_telemetry_alert_taquicardia():
    """Valida se o limite clínico de taquicardia dispara alerta devidamente (> 100 bpm)."""
    payload = {
        "temperatura": 36.5,
        "frequencia_cardiaca": 115
    }
    response = client.post("/api/telemetry", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["telemetry"]["alerta"] is True
    assert "Taquicardia" in json_data["telemetry"]["mensagem_alerta"]

def test_update_telemetry_alert_febre():
    """Valida se o limite clínico de febre dispara alerta devidamente (> 38.0°C)."""
    payload = {
        "temperatura": 38.5,
        "frequencia_cardiaca": 75
    }
    response = client.post("/api/telemetry", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["telemetry"]["alerta"] is True
    assert "Febre" in json_data["telemetry"]["mensagem_alerta"]

def test_get_latest_telemetry():
    """Valida a leitura da última telemetria registrada em memória."""
    payload = {
        "temperatura": 37.0,
        "frequencia_cardiaca": 85
    }
    client.post("/api/telemetry", json=payload)
    
    response = client.get("/api/telemetry/latest")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["temperatura"] == 37.0
    assert json_data["frequencia_cardiaca"] == 85

def test_predict_risk_endpoint():
    """Valida a inferência do modelo de ML direto via API."""
    payload = {
        "idade": 65,
        "frequencia_cardiaca": 95,
        "spo2": 93,
        "carga_sistema": 0.5,
        "disponibilidade_recursos": 0.5,
        "historico_cardiaco": 1
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert "probabilidade" in json_data
    assert "classificacao" in json_data
    assert json_data["classificacao"] in ["Alto Risco", "Baixo Risco"]

def test_analyze_patient_endpoint_mocked(monkeypatch):
    """Valida o acionamento de múltiplos agentes de IA mockando a chamada externa de LLM."""
    
    # Definição de mocks para simular as estruturas de retorno dos agentes
    class MockAgent:
        name = "Agente Orquestrador CardioIA"
        
    class MockResult:
        last_agent = MockAgent()
        final_output = """**Recomendação Final de Risco Cardíaco**

*   **Probabilidade Prevista:** 85.00%
*   **Classificação de Risco:** Alto Risco
*   **Protocolos Sugeridos:**
    *   Monitoramento contínuo em UTI.
    *   Administração imediata de antiagregantes plaquetários.
*   **Justificativa Clínica:** O paciente apresenta risco elevado devido à idade e histórico cardíaco."""

    async def mock_run_cardioia(patient_data):
        return MockResult()

    # Aplica o mock na função da API
    monkeypatch.setattr("app.run_cardioia", mock_run_cardioia)

    payload = {
        "idade": 65,
        "frequencia_cardiaca": 95,
        "spo2": 93,
        "carga_sistema": 0.5,
        "disponibilidade_recursos": 0.5,
        "historico_cardiaco": 1
    }
    
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    
    # Asserções de conformidade de formato de resposta parsed dos agentes
    assert json_data["agente_final"] == "Agente Orquestrador CardioIA"
    assert "Alto Risco" in json_data["dados_analisados"]["classificacao"]
    assert "85.00%" in json_data["dados_analisados"]["probabilidade"]
    assert len(json_data["dados_analisados"]["protocolos"]) == 2
    assert "Monitoramento contínuo em UTI." in json_data["dados_analisados"]["protocolos"]
