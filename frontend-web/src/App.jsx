import React, { useState, useEffect, useRef } from 'react';
import { 
  Heart, 
  Thermometer, 
  Activity, 
  AlertTriangle, 
  ShieldAlert, 
  UserCheck, 
  Cpu, 
  RefreshCw, 
  ClipboardList, 
  TrendingUp, 
  Radio
} from 'lucide-react';
import './App.css';

// Configuração do host da API local
const API_BASE_URL = 'http://localhost:8000';

function App() {
  // Estados de Conexão e Telemetria
  const [apiStatus, setApiStatus] = useState('offline'); // online | simulated | offline
  const [telemetry, setTelemetry] = useState({
    temperatura: 36.5,
    frequencia_cardiaca: 80,
    timestamp: null,
    alerta: false,
    mensagem_alerta: 'Sinais vitais normais.'
  });
  const [telemetryHistory, setTelemetryHistory] = useState([
    { fc: 72, temp: 36.4 },
    { fc: 75, temp: 36.5 },
    { fc: 78, temp: 36.5 },
    { fc: 80, temp: 36.6 },
    { fc: 79, temp: 36.5 },
    { fc: 81, temp: 36.6 },
    { fc: 83, temp: 36.7 },
    { fc: 80, temp: 36.5 }
  ]);

  // Estados de Operação da API
  const [loading, setLoading] = useState(false);
  const [loadingType, setLoadingType] = useState(''); // ml | agent
  const [error, setError] = useState(null);
  
  // Estado do Formulário
  const [formData, setFormData] = useState({
    idade: 68,
    frequencia_cardiaca: 95,
    spo2: 92,
    carga_sistema: 0.7,
    disponibilidade_recursos: 0.5,
    historico_cardiaco: 1
  });

  // Estado dos Resultados
  const [analysisResult, setAnalysisResult] = useState(null);

  // Intervalo de Polling
  const pollingRef = useRef(null);

  // 1. Monitorar Status do Backend e Configurar Polling
  useEffect(() => {
    const checkApiAndPoll = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (response.ok) {
          setApiStatus('online');
          fetchTelemetry();
        } else {
          startSimulation();
        }
      } catch (err) {
        startSimulation();
      }
    };

    const fetchTelemetry = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/telemetry/latest`);
        if (response.ok) {
          const data = await response.json();
          // Atualiza a telemetria com os dados do backend
          setTelemetry(data);
          
          // Adiciona ao histórico do gráfico
          setTelemetryHistory(prev => {
            const nextHistory = [...prev, { fc: data.frequencia_cardiaca, temp: data.temperatura }];
            if (nextHistory.length > 15) nextHistory.shift();
            return nextHistory;
          });
        }
      } catch (err) {
        console.error('Erro ao consultar telemetria do backend:', err);
      }
    };

    const startSimulation = () => {
      setApiStatus('simulated');
      // Limpa polling do backend se houver
      if (pollingRef.current) clearInterval(pollingRef.current);
      
      // Configura geração de dados simulados locais
      pollingRef.current = setInterval(() => {
        setTelemetry(prev => {
          // Pequena flutuação aleatória
          const fcDelta = Math.floor(Math.random() * 9) - 4; // -4 a 4
          const tempDelta = (Math.random() * 0.4) - 0.2; // -0.2 a 0.2
          
          let nextFc = prev.frequencia_cardiaca + fcDelta;
          if (nextFc < 55) nextFc = 60;
          if (nextFc > 115) nextFc = 100;
          
          let nextTemp = parseFloat((prev.temperatura + tempDelta).toFixed(1));
          if (nextTemp < 35.8) nextTemp = 36.2;
          if (nextTemp > 39.2) nextTemp = 37.5;
          
          // Validação de alertas simulados
          let alerta = false;
          let mensagem_alerta = 'Sinais vitais normais.';
          if (nextFc > 100) {
            alerta = true;
            mensagem_alerta = 'Alerta de Saúde: Taquicardia detectada!';
          } else if (nextFc < 50) {
            alerta = true;
            mensagem_alerta = 'Alerta de Saúde: Bradicardia detectada!';
          } else if (nextTemp > 38.0) {
            alerta = true;
            mensagem_alerta = 'Alerta de Saúde: Febre detectada!';
          }
          
          const newPoint = {
            temperatura: nextTemp,
            frequencia_cardiaca: nextFc,
            timestamp: new Date().toISOString(),
            alerta,
            mensagem_alerta
          };
          
          // Adiciona ao histórico do gráfico
          setTelemetryHistory(hist => {
            const nextHistory = [...hist, { fc: nextFc, temp: nextTemp }];
            if (nextHistory.length > 15) nextHistory.shift();
            return nextHistory;
          });

          return newPoint;
        });
      }, 3000);
    };

    // Inicializa a verificação
    checkApiAndPoll();
    
    // Define o intervalo de polling para dados reais se a API estiver online
    const realApiInterval = setInterval(() => {
      if (apiStatus === 'online') {
        fetchTelemetry();
      } else if (apiStatus === 'offline') {
        checkApiAndPoll();
      }
    }, 3000);

    return () => {
      clearInterval(realApiInterval);
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [apiStatus]);

  // Função para sincronizar dados da telemetria com o formulário
  const syncTelemetryToForm = () => {
    setFormData(prev => ({
      ...prev,
      frequencia_cardiaca: telemetry.frequencia_cardiaca
    }));
  };

  // Alterações no Formulário
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'idade' || name === 'frequencia_cardiaca' || name === 'spo2' || name === 'historico_cardiaco' 
        ? parseInt(value) || 0 
        : parseFloat(value) || 0.0
    }));
  };

  // 2. Chamar Predição de Risco Rápida (ML)
  const handlePredictML = async (e) => {
    e.preventDefault();
    setLoading(true);
    setLoadingType('ml');
    setError(null);
    setAnalysisResult(null);

    // Se a API estiver simulada ou offline, criamos um resultado local para demonstração
    if (apiStatus === 'simulated') {
      setTimeout(() => {
        // Lógica de predição simples local
        const score = calcularScoreSimulado(formData);
        setAnalysisResult({
          type: 'ml',
          probabilidade: `${(score * 100).toFixed(2)}%`,
          probabilidade_float: score,
          classificacao: score > 0.6 ? 'Alto Risco' : 'Baixo Risco',
          protocolos: score > 0.6 
            ? ['Monitoramento contínuo em UTI.', 'Administração imediata de antiagregantes plaquetários.', 'Acionamento da equipe de hemodinâmica.']
            : ['Observação em enfermaria.', 'Realização de ECG seriado.', 'Avaliação cardiológica ambulatorial.'],
          justificativa: `Simulação Local: O paciente com ${formData.idade} anos apresenta probabilidade estimada em ${(score * 100).toFixed(2)}% baseada na frequência cardíaca de ${formData.frequencia_cardiaca} bpm e saturação de ${formData.spo2}%.`
        });
        setLoading(false);
      }, 1000);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (!response.ok) throw new Error('Falha na resposta do servidor API');
      
      const data = await response.json();
      
      setAnalysisResult({
        type: 'ml',
        probabilidade: data.probabilidade,
        probabilidade_float: data.probabilidade_float,
        classificacao: data.classificacao,
        protocolos: data.classificacao === 'Alto Risco'
          ? ['Monitoramento contínuo em UTI.', 'Administração imediata de antiagregantes plaquetários.', 'Acionamento da equipe de hemodinâmica.']
          : ['Observação em enfermaria.', 'Realização de ECG seriado.', 'Avaliação cardiológica ambulatorial.'],
        justificativa: `Modelo CardioIA (Random Forest): Análise computada com base nas variáveis clínicas fornecidas. O paciente apresenta frequência cardíaca de ${formData.frequencia_cardiaca} bpm e saturação de O2 de ${formData.spo2}%, resultando em classificação de ${data.classificacao}.`
      });
    } catch (err) {
      setError(`Erro ao executar predição: ${err.message}. Certifique-se de que o backend FastAPI está rodando.`);
    } finally {
      setLoading(false);
    }
  };

  // 3. Chamar Análise Preditiva Avançada (Multiagentes)
  const handleAnalyzeAgents = async (e) => {
    e.preventDefault();
    setLoading(true);
    setLoadingType('agent');
    setError(null);
    setAnalysisResult(null);

    // Se a API estiver simulada ou offline, criamos um resultado simulado completo de IA
    if (apiStatus === 'simulated') {
      setTimeout(() => {
        const score = calcularScoreSimulado(formData);
        const classificacao = score > 0.6 ? 'Alto Risco' : 'Baixo Risco';
        const probabilidadeStr = `${(score * 100).toFixed(2)}%`;
        
        setAnalysisResult({
          type: 'agent',
          agente_final: 'Agente Orquestrador CardioIA',
          probabilidade: probabilidadeStr,
          probabilidade_float: score,
          classificacao: classificacao,
          protocolos: classificacao === 'Alto Risco'
            ? ['Monitoramento contínuo em UTI.', 'Administração imediata de antiagregantes plaquetários.', 'Acionamento da equipe de hemodinâmica.']
            : ['Observação em enfermaria.', 'Realização de ECG seriado.', 'Avaliação cardiológica ambulatorial.'],
          justificativa: `Simulação Local (Multiagente): O Agente Analista de Risco executou a inferência no modelo RandomForest encontrando score de ${probabilidadeStr}. Em seguida, o Agente Especialista em Protocolos selecionou a conduta clínica adequada para ${classificacao}. O orquestrador concluiu o relatório justificando que a idade (${formData.idade} anos) aliada a ${formData.frequencia_cardiaca} bpm representam um risco relevante ao paciente.`,
          relatorio_markdown: `### Relatório Clínico CardioIA (Simulação)
*   **Probabilidade Prevista:** ${probabilidadeStr}
*   **Classificação de Risco:** ${classificacao}
*   **Protocolos Sugeridos:**
    ${classificacao === 'Alto Risco' 
      ? '* Monitoramento contínuo em UTI.\n    * Administração imediata de antiagregantes plaquetários.\n    * Acionamento da equipe de hemodinâmica.'
      : '* Observação em enfermaria.\n    * Realização de ECG seriado.\n    * Avaliação cardiológica ambulatorial.'}
*   **Justificativa Clínica:** O paciente apresenta risco classificado como ${classificacao}. Com base em idade (${formData.idade} anos) e histórico, o sistema recomenda a imediata aplicação do protocolo correspondente.`
        });
        setLoading(false);
      }, 1500);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (!response.ok) throw new Error('Falha na resposta do servidor de agentes inteligentes');
      
      const data = await response.json();
      
      setAnalysisResult({
        type: 'agent',
        agente_final: data.agente_final,
        probabilidade: data.dados_analisados.probabilidade,
        probabilidade_float: parseFloat(data.dados_analisados.probabilidade) / 100 || 0.5,
        classificacao: data.dados_analisados.classificacao,
        protocolos: data.dados_analisados.protocolos,
        justificativa: data.dados_analisados.justificativa,
        relatorio_markdown: data.relatorio_markdown
      });
    } catch (err) {
      setError(`Erro ao executar sistema multiagente: ${err.message}. Certifique-se de que a chave do Gemini está configurada no .env e o backend FastAPI está ativo.`);
    } finally {
      setLoading(false);
    }
  };

  // Cálculo de Score Simulador Local (Fallback)
  const calcularScoreSimulado = (data) => {
    let score = 0.1;
    if (data.idade > 60) score += 0.15;
    if (data.frequencia_cardiaca > 90) score += 0.25;
    if (data.frequencia_cardiaca > 110) score += 0.15;
    if (data.spo2 < 93) score += 0.25;
    if (data.historico_cardiaco === 1) score += 0.2;
    // Garante limites entre 0.05 e 0.98
    return Math.max(0.05, Math.min(0.98, score));
  };

  // 4. Geração dos caminhos (Path) do Gráfico SVG
  const generateChartPath = () => {
    if (telemetryHistory.length === 0) return '';
    const width = 500;
    const height = 140;
    const padding = 10;
    
    const pointsCount = telemetryHistory.length;
    const stepX = (width - padding * 2) / (pointsCount - 1);
    
    // Mapeamento: FC de 40 a 140 bpm para Y de height a 0
    return telemetryHistory.map((pt, index) => {
      const x = padding + index * stepX;
      // Normaliza
      const normalizedFc = Math.max(40, Math.min(140, pt.fc));
      const percentage = (normalizedFc - 40) / 100; // 0 a 1
      const y = height - padding - percentage * (height - padding * 2);
      return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
    }).join(' ');
  };

  const generateChartAreaPath = (linePath) => {
    if (!linePath) return '';
    const width = 500;
    const height = 140;
    const padding = 10;
    const pointsCount = telemetryHistory.length;
    const stepX = (width - padding * 2) / (pointsCount - 1);
    
    const lastX = padding + (pointsCount - 1) * stepX;
    return `${linePath} L ${lastX} ${height - padding} L ${padding} ${height - padding} Z`;
  };

  const linePath = generateChartPath();
  const areaPath = generateChartAreaPath(linePath);
  
  // Obter coordenadas do último ponto para o marcador piscante
  const getLastPointCoords = () => {
    if (telemetryHistory.length === 0) return { x: 0, y: 0 };
    const width = 500;
    const height = 140;
    const padding = 10;
    const pointsCount = telemetryHistory.length;
    const stepX = (width - padding * 2) / (pointsCount - 1);
    
    const lastIndex = pointsCount - 1;
    const lastPt = telemetryHistory[lastIndex];
    
    const x = padding + lastIndex * stepX;
    const normalizedFc = Math.max(40, Math.min(140, lastPt.fc));
    const percentage = (normalizedFc - 40) / 100;
    const y = height - padding - percentage * (height - padding * 2);
    
    return { x, y };
  };

  const lastCoords = getLastPointCoords();

  // Configuração do Gauge Circular de Risco
  const strokeDashoffset = analysisResult 
    ? 251.2 - (251.2 * (analysisResult.probabilidade_float || 0))
    : 251.2;

  const isRiskAlto = analysisResult && (analysisResult.classificacao.toLowerCase().includes('alto') || analysisResult.probabilidade_float > 0.6);

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand-section">
          <Heart className="brand-icon" size={32} />
          <h1 className="brand-title">CardioIA</h1>
        </div>
        
        <div className="status-badge">
          <Radio size={14} className={apiStatus === 'online' ? 'heartbeat-icon' : ''} />
          <span>Status API:</span>
          <div className={`status-dot ${apiStatus}`} />
          <span style={{ textTransform: 'capitalize', fontWeight: 'bold', color: apiStatus === 'online' ? '#00e676' : '#8a2be2' }}>
            {apiStatus === 'online' ? 'Online' : apiStatus === 'simulated' ? 'Simulado' : 'Verificando'}
          </span>
        </div>
      </header>

      {/* Main Grid */}
      <div className="dashboard-grid">
        
        {/* Lado Esquerdo: Telemetria IoT e Gráfico */}
        <div className="dashboard-panel">
          <h2 className="panel-title">
            <Activity size={18} />
            Monitoramento IoT em Tempo Real
          </h2>

          {/* Banner de Alerta Crítico */}
          {telemetry.alerta && (
            <div className="alert-banner">
              <AlertTriangle className="alert-icon" size={24} />
              <div className="alert-content">
                <h4>ALERTA CLÍNICO ATIVO</h4>
                <p>{telemetry.mensagem_alerta}</p>
              </div>
            </div>
          )}

          {/* Widgets Numéricos */}
          <div className="telemetry-row">
            {/* Widget de Batimentos */}
            <div className={`glass-card telemetry-widget ${telemetry.frequencia_cardiaca > 100 || telemetry.frequencia_cardiaca < 50 ? 'danger' : ''}`}>
              <div className="telemetry-header">
                <Heart size={16} className={telemetry.frequencia_cardiaca > 100 || telemetry.frequencia_cardiaca < 50 ? 'heartbeat-icon' : 'text-muted'} />
                <span>Batimentos Cardíacos</span>
              </div>
              <div className="telemetry-value-container">
                <span className="telemetry-value">{telemetry.frequencia_cardiaca}</span>
                <span className="telemetry-unit">BPM</span>
              </div>
              <span className="telemetry-status">
                {telemetry.frequencia_cardiaca > 100 ? 'Taquicardia' : telemetry.frequencia_cardiaca < 50 ? 'Bradicardia' : 'Normal'}
              </span>
            </div>

            {/* Widget de Temperatura */}
            <div className={`glass-card telemetry-widget ${telemetry.temperatura > 38.0 || telemetry.temperatura < 35.0 ? 'danger' : ''}`}>
              <div className="telemetry-header">
                <Thermometer size={16} />
                <span>Temperatura</span>
              </div>
              <div className="telemetry-value-container">
                <span className="telemetry-value">{telemetry.temperatura}</span>
                <span className="telemetry-unit">°C</span>
              </div>
              <span className="telemetry-status">
                {telemetry.temperatura > 38.0 ? 'Febre' : telemetry.temperatura < 35.0 ? 'Hipotermia' : 'Normal'}
              </span>
            </div>
          </div>

          {/* Gráfico de Linha em Tempo Real */}
          <div className="glass-card">
            <div className="telemetry-header" style={{ marginBottom: '1.25rem', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <TrendingUp size={16} />
                <span>Frequência Cardíaca (Evolução)</span>
              </div>
              <span style={{ fontSize: '0.75rem', opacity: 0.5 }}>Últimas 15 leituras</span>
            </div>
            
            <div className="chart-container">
              <svg className="chart-svg" viewBox="0 0 500 140" preserveAspectRatio="none">
                <defs>
                  {/* Gradiente de fundo cyan normal */}
                  <linearGradient id="chart-gradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--accent-cyan)" stopOpacity="0.4" />
                    <stop offset="100%" stopColor="var(--accent-cyan)" stopOpacity="0.0" />
                  </linearGradient>
                  
                  {/* Gradiente de fundo vermelho alerta */}
                  <linearGradient id="chart-gradient-danger" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--accent-red)" stopOpacity="0.4" />
                    <stop offset="100%" stopColor="var(--accent-red)" stopOpacity="0.0" />
                  </linearGradient>
                </defs>

                {/* Linhas de Grade de Background */}
                <line x1="0" y1="20" x2="500" y2="20" className="grid-line" />
                <line x1="0" y1="55" x2="500" y2="55" className="grid-line" />
                <line x1="0" y1="90" x2="500" y2="90" className="grid-line" />
                <line x1="0" y1="120" x2="500" y2="120" className="grid-line" />

                {/* Preenchimento de Área */}
                {areaPath && (
                  <path 
                    d={areaPath} 
                    className={`chart-area ${telemetry.frequencia_cardiaca > 100 || telemetry.frequencia_cardiaca < 50 ? 'danger' : ''}`} 
                  />
                )}

                {/* Linha do Gráfico */}
                {linePath && (
                  <path 
                    d={linePath} 
                    className={`chart-line ${telemetry.frequencia_cardiaca > 100 || telemetry.frequencia_cardiaca < 50 ? 'danger' : ''}`} 
                  />
                )}

                {/* Marcador do Ponto Atual */}
                {telemetryHistory.length > 0 && (
                  <circle 
                    cx={lastCoords.x} 
                    cy={lastCoords.y} 
                    r="5" 
                    className={`chart-marker ${telemetry.frequencia_cardiaca > 100 || telemetry.frequencia_cardiaca < 50 ? 'danger' : ''}`} 
                  />
                )}
              </svg>
            </div>
          </div>
          
          <button 
            className="btn btn-secondary" 
            onClick={syncTelemetryToForm}
            style={{ padding: '0.6rem', fontSize: '0.85rem' }}
          >
            <RefreshCw size={14} />
            Enviar Frequência Recente do IoT para Formulário
          </button>
        </div>

        {/* Lado Direito: Entrada e Análise Preditiva */}
        <div className="dashboard-panel">
          <h2 className="panel-title">
            <ShieldAlert size={18} />
            Central de Inteligência Clínica (Previsão)
          </h2>

          <div className="glass-card">
            <h3 style={{ fontSize: '1rem', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <UserCheck size={16} />
              Variáveis Clínicas do Paciente
            </h3>
            
            <form onSubmit={(e) => e.preventDefault()}>
              <div className="patient-form">
                <div className="form-group">
                  <label htmlFor="idade">Idade</label>
                  <input
                    type="number"
                    id="idade"
                    name="idade"
                    className="form-control"
                    value={formData.idade}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="frequencia_cardiaca">Frequência Cardíaca (bpm)</label>
                  <input
                    type="number"
                    id="frequencia_cardiaca"
                    name="frequencia_cardiaca"
                    className="form-control"
                    value={formData.frequencia_cardiaca}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="spo2">Saturação SPO2 (%)</label>
                  <input
                    type="number"
                    id="spo2"
                    name="spo2"
                    className="form-control"
                    value={formData.spo2}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="carga_sistema">Carga do Sistema (0 a 1)</label>
                  <input
                    type="number"
                    step="0.1"
                    id="carga_sistema"
                    name="carga_sistema"
                    className="form-control"
                    value={formData.carga_sistema}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="disponibilidade_recursos">Disponibilidade Recursos (0 a 1)</label>
                  <input
                    type="number"
                    step="0.1"
                    id="disponibilidade_recursos"
                    name="disponibilidade_recursos"
                    className="form-control"
                    value={formData.disponibilidade_recursos}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="historico_cardiaco">Histórico Cardíaco</label>
                  <select
                    id="historico_cardiaco"
                    name="historico_cardiaco"
                    className="form-control"
                    value={formData.historico_cardiaco}
                    onChange={handleInputChange}
                  >
                    <option value={1}>Sim (1)</option>
                    <option value={0}>Não (0)</option>
                  </select>
                </div>
              </div>

              <div className="button-row">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  disabled={loading}
                  onClick={handlePredictML}
                >
                  <Cpu size={16} />
                  Inferência Rápida (ML)
                </button>
                
                <button 
                  type="button" 
                  className="btn btn-primary" 
                  disabled={loading}
                  onClick={handleAnalyzeAgents}
                >
                  <Heart className="heartbeat-icon" size={16} style={{ color: '#080b11' }} />
                  Análise Multiagente (IA)
                </button>
              </div>
            </form>
          </div>

          {/* Loader e Status de Carregamento */}
          {loading && (
            <div className="glass-card loading-state">
              <div className={`spinner ${loadingType === 'agent' ? 'purple' : ''}`} />
              <p className="loading-text">
                {loadingType === 'agent' 
                  ? 'Orquestrando Agentes Inteligentes (Gemini SDK)...' 
                  : 'Computando inferência no modelo RandomForest...'}
              </p>
            </div>
          )}

          {/* Tratamento de Erros da API */}
          {error && (
            <div className="glass-card" style={{ borderColor: 'var(--accent-red-border)', background: 'rgba(255, 51, 102, 0.05)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-red)', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                <AlertTriangle size={18} />
                <span>Erro de Processamento</span>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{error}</p>
            </div>
          )}

          {/* Exibição de Resultados */}
          {analysisResult && (
            <div className="glass-card results-card">
              <div className="results-header-row">
                <div className="risk-level-display">
                  <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Classificação:</span>
                  <span className={`risk-badge ${isRiskAlto ? 'alto' : 'baixo'}`}>
                    {analysisResult.classificacao}
                  </span>
                </div>
                
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.05)', padding: '0.3rem 0.6rem', borderRadius: '4px' }}>
                  Motor: {analysisResult.type === 'agent' ? 'Multiagentes (Gemini)' : 'Modelo ML (RandomForest)'}
                </span>
              </div>

              <div className="results-container">
                {/* Gauge Circular */}
                <div className="circular-gauge-wrapper">
                  <span className="gauge-title">Score Risco</span>
                  <svg className="gauge-svg" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="40" className="gauge-bg" />
                    <circle 
                      cx="50" 
                      cy="50" 
                      r="40" 
                      className={`gauge-fill ${isRiskAlto ? 'alto' : ''}`} 
                      strokeDasharray="251.2" 
                      strokeDashoffset={strokeDashoffset} 
                    />
                    <text x="50" y="52" className={`gauge-text ${isRiskAlto ? 'alto' : ''}`}>
                      {analysisResult.probabilidade}
                    </text>
                  </svg>
                </div>

                {/* Protocolos */}
                <div className="protocols-section">
                  <span className="protocols-title">
                    <ClipboardList size={14} style={{ verticalAlign: 'middle', marginRight: '0.25rem' }} />
                    Protocolos Clínicos Recomendados
                  </span>
                  <ul className="protocol-list">
                    {analysisResult.protocolos.map((protocol, i) => (
                      <li key={i} className="protocol-item">
                        <div className={`protocol-check ${isRiskAlto ? 'danger' : ''}`}>✓</div>
                        <span>{protocol}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Relatório Justificativa */}
                <div className="report-section">
                  <span className="report-title">Parecer do Orquestrador e Justificativa</span>
                  <div className="report-text" style={{ whiteSpace: 'pre-line' }}>
                    {analysisResult.justificativa}
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

export default App;
