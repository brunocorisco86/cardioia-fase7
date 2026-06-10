import os
import sys
import datetime
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import uvicorn

# Adiciona o diretório atual ao path para garantir que importações de módulos locais funcionem
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Configura o logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cardioia-backend")

# Inicialização tardia/segura dos agentes
run_cardioia = None
ml_model = None

def load_ml_model():
    global ml_model
    if ml_model is None:
        try:
            model_path = os.path.join(BASE_DIR, "modelo_cardioia.pkl")
            if os.path.exists(model_path):
                ml_model = joblib.load(model_path)
                logger.info("Modelo de Machine Learning carregado com sucesso.")
            else:
                logger.warning(f"Arquivo do modelo não encontrado em: {model_path}")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo de ML: {str(e)}")

# Tenta carregar o modelo de ML
load_ml_model()

# Tenta importar run_cardioia de cardioia_agents
try:
    from cardioia_agents import run_cardioia
    logger.info("Módulo cardioia_agents importado com sucesso.")
except Exception as e:
    logger.error(f"Não foi possível importar cardioia_agents: {str(e)}")

app = FastAPI(
    title="CardioIA API",
    description="API de Integração para Previsão de Risco Cardíaco, Sistema Multiagente e Telemetria IoT",
    version="1.0.0"
)

# Configurando CORS para permitir conexões do frontend Web e App mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, deve ser restrito aos domínios das interfaces
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estado temporário em memória para armazenar a telemetria mais recente do IoT (temperatura e batimentos)
latest_telemetry = {
    "temperatura": 36.5,
    "frequencia_cardiaca": 80,
    "timestamp": None,
    "alerta": False,
    "mensagem_alerta": "Sinais vitais normais."
}

# Modelo de entrada para telemetria IoT
class TelemetryInput(BaseModel):
    temperatura: float = Field(..., description="Temperatura corporal medida pelo sensor")
    frequencia_cardiaca: int = Field(..., description="Frequência cardíaca medida em bpm")

# Modelo de entrada para predição e análise do paciente
class PatientInput(BaseModel):
    idade: int = Field(..., description="Idade do paciente")
    frequencia_cardiaca: int = Field(..., description="Frequência cardíaca (bpm)")
    spo2: int = Field(..., description="Saturação de oxigênio (SPO2 %)")
    carga_sistema: float = Field(0.5, description="Carga do sistema de atendimento hospitalar (0 a 1)")
    disponibilidade_recursos: float = Field(0.5, description="Disponibilidade de recursos hospitalares (0 a 1)")
    historico_cardiaco: int = Field(0, description="Histórico de eventos cardíacos (1 para sim, 0 para não)")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "CardioIA API",
        "description": "API de Integração para a Plataforma CardioIA",
        "version": "1.0.0"
    }

@app.post("/api/telemetry")
def update_telemetry(data: TelemetryInput):
    """
    Recebe os sinais vitais coletados em tempo real pelo hardware IoT (MicroPython).
    Aplica limites clínicos básicos para acionar alertas visuais ou sonoros imediatos.
    """
    global latest_telemetry
    
    alerta = False
    mensagem_alerta = "Sinais vitais normais."
    
    # Validações clínicas simplificadas para alertas imediatos
    if data.frequencia_cardiaca > 100:
        alerta = True
        mensagem_alerta = "Alerta de Saúde: Taquicardia detectada!"
    elif data.frequencia_cardiaca < 50:
        alerta = True
        mensagem_alerta = "Alerta de Saúde: Bradicardia detectada!"
        
    if data.temperatura > 38.0:
        alerta = True
        mensagem_alerta = "Alerta de Saúde: Febre detectada!"
    elif data.temperatura < 35.0:
        alerta = True
        mensagem_alerta = "Alerta de Saúde: Hipotermia detectada!"
        
    latest_telemetry = {
        "temperatura": data.temperatura,
        "frequencia_cardiaca": data.frequencia_cardiaca,
        "timestamp": datetime.datetime.now().isoformat(),
        "alerta": alerta,
        "mensagem_alerta": mensagem_alerta
    }
    
    logger.info(f"Telemetria recebida - Temp: {data.temperatura}°C, FC: {data.frequencia_cardiaca} bpm. Alerta: {alerta}")
    
    return {
        "status": "success",
        "message": "Telemetria gravada com sucesso",
        "telemetry": latest_telemetry
    }

@app.get("/api/telemetry/latest")
def get_latest_telemetry():
    """
    Retorna os dados de telemetria mais recentes gravados na memória do servidor.
    Será consumido pelo dashboard Web/Mobile de forma contínua (pooling).
    """
    return latest_telemetry

@app.post("/api/predict")
def predict_risk_endpoint(patient: PatientInput):
    """
    Realiza a inferência direta utilizando o modelo preditivo de Machine Learning (`modelo_cardioia.pkl`).
    Calcula a probabilidade de risco clínico de forma síncrona e rápida.
    """
    global ml_model
    if ml_model is None:
        load_ml_model()
    if ml_model is None:
        raise HTTPException(status_code=500, detail="Modelo preditivo não pôde ser carregado no servidor.")
        
    try:
        # Prepara a entrada no formato que o Scikit-learn espera
        input_df = pd.DataFrame([{
            'idade': patient.idade,
            'frequencia_cardiaca': patient.frequencia_cardiaca,
            'spo2': patient.spo2,
            'carga_sistema': patient.carga_sistema,
            'disponibilidade_recursos': patient.disponibilidade_recursos,
            'historico_cardiaco': patient.historico_cardiaco,
        }])
        
        # Realiza a predição da probabilidade de risco (classe 1)
        prob = ml_model.predict_proba(input_df)[0][1]
        classification = "Alto Risco" if prob > 0.6 else "Baixo Risco"
        
        return {
            "probabilidade": f"{prob:.2%}",
            "probabilidade_float": float(prob),
            "classificacao": classification
        }
    except Exception as e:
        logger.error(f"Erro ao computar inferência no endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar inferência de risco: {str(e)}")

@app.post("/api/analyze")
async def analyze_patient_endpoint(patient: PatientInput):
    """
    Executa o ecossistema multiagente (Orquestrador, Analista de Risco e Especialista).
    Retorna o relatório médico final completo gerado pela IA.
    """
    global run_cardioia
    if run_cardioia is None:
        # Tenta re-importar se tiver falhado anteriormente
        try:
            from cardioia_agents import run_cardioia
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Módulo de agentes inteligentes indisponível no servidor: {str(e)}")
            
    patient_dict = {
        'idade': patient.idade,
        'frequencia_cardiaca': patient.frequencia_cardiaca,
        'spo2': patient.spo2,
        'carga_sistema': patient.carga_sistema,
        'disponibilidade_recursos': patient.disponibilidade_recursos,
        'historico_cardiaco': patient.historico_cardiaco,
    }
    
    try:
        logger.info(f"Acionando sistema multiagente para paciente de {patient.idade} anos.")
        result = await run_cardioia(patient_dict)
        
        # Executa o parseamento da saída para estruturar no JSON de resposta
        final_text = result.final_output
        probabilidade = "N/A"
        classificacao = "N/A"
        protocolos = []
        justificativa = ""
        
        import re
        
        # Expressões regulares para mapear o conteúdo gerado
        prob_match = re.search(r"\*\*Probabilidade\s+Prevista:\*\*\s*(.+)", final_text, re.IGNORECASE)
        class_match = re.search(r"\*\*Classificação\s+de\s+Risco:\*\*\s*(.+)", final_text, re.IGNORECASE)
        just_match = re.search(r"\*\*Justificativa\s+Clínica:\*\*\s*(.+)", final_text, re.IGNORECASE | re.DOTALL)
        
        if prob_match:
            probabilidade = prob_match.group(1).strip()
        if class_match:
            classificacao = class_match.group(1).strip()
        if just_match:
            justificativa = just_match.group(1).strip()
            
        # Tenta isolar a seção de protocolos sugeridos e quebrá-la em lista
        proto_block_match = re.search(r"\*\*Protocolos\s+Sugeridos:\*\*(.*?)(?=\*\*Justificativa|\Z)", final_text, re.IGNORECASE | re.DOTALL)
        if proto_block_match:
            proto_lines = proto_block_match.group(1).split('\n')
            for line in proto_lines:
                clean_line = line.strip().replace('*', '').replace('-', '').strip()
                if clean_line:
                    protocolos.append(clean_line)
                    
        # Filtro de segurança/fallback para garantir estrutura de protocolos se o regex falhar
        if not protocolos:
            if "Alto" in classificacao:
                protocolos = [
                    "Monitoramento contínuo em UTI.",
                    "Administração imediata de antiagregantes plaquetários.",
                    "Acionamento da equipe de hemodinâmica."
                ]
            else:
                protocolos = [
                    "Observação em enfermaria.",
                    "Realização de ECG seriado.",
                    "Avaliação cardiológica ambulatorial."
                ]
                
        return {
            "agente_final": result.last_agent.name if result.last_agent else "Agente Orquestrador CardioIA",
            "relatorio_markdown": final_text,
            "dados_analisados": {
                "probabilidade": probabilidade,
                "classificacao": classificacao,
                "protocolos": protocolos,
                "justificativa": justificativa
            }
        }
    except Exception as e:
        logger.error(f"Erro na execução da análise multiagente: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno no pipeline multiagente: {str(e)}")

if __name__ == "__main__":
    # Inicia o servidor uvicorn localmente na porta 8000
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
