import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  StatusBar,
  ActivityIndicator,
  Dimensions
} from 'react-native';
import { 
  Heart, 
  Thermometer, 
  Activity, 
  AlertTriangle, 
  ShieldAlert, 
  User, 
  Lock, 
  LogOut,
  TrendingUp,
  Cpu,
  RefreshCw,
  Sliders,
  CheckCircle2
} from 'lucide-react-native';

const API_BASE_URL = 'http://10.0.2.2:8000'; // IP para acessar o localhost da máquina a partir do emulador Android

export default function App() {
  // Navegação básica
  const [currentScreen, setCurrentScreen] = useState('login'); // login | dashboard

  // Estados de Login
  const [email, setEmail] = useState('paciente@cardioia.com.br');
  const [password, setPassword] = useState('123456');
  const [loginError, setLoginError] = useState('');

  // Estados de Telemetria
  const [apiStatus, setApiStatus] = useState('checking'); // online | simulated
  const [telemetry, setTelemetry] = useState({
    temperatura: 36.4,
    frequencia_cardiaca: 72,
    timestamp: null,
    alerta: false,
    mensagem_alerta: 'Sinais vitais normais.'
  });
  const [telemetryHistory, setTelemetryHistory] = useState([
    70, 71, 73, 75, 76, 75, 73, 71, 69, 68, 69, 71, 73, 75, 74
  ]);

  // Estados do Formulário e Predição
  const [formData, setFormData] = useState({
    idade: 45,
    frequencia_cardiaca: 72,
    spo2: 98,
    carga_sistema: 0.5,
    disponibilidade_recursos: 0.6,
    historico_cardiaco: 0
  });

  const [loading, setLoading] = useState(false);
  const [loadingType, setLoadingType] = useState(''); // ml | agent
  const [predictionResult, setPredictionResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  const simTickRef = useRef(0);
  const intervalRef = useRef(null);

  // 1. Efeito de Telemetria em Tempo Real (Polling ou Simulação)
  useEffect(() => {
    if (currentScreen !== 'dashboard') {
      if (intervalRef.current) clearInterval(intervalRef.current);
      return;
    }

    const checkApiAndPoll = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (response.ok) {
          setApiStatus('online');
          fetchLatestTelemetry();
        } else {
          startLocalSimulation();
        }
      } catch (err) {
        startLocalSimulation();
      }
    };

    const fetchLatestTelemetry = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/telemetry/latest`);
        if (response.ok) {
          const data = await response.json();
          setTelemetry(data);
          
          // Atualiza dados de formulário com os batimentos reais
          setFormData(prev => ({ ...prev, frequencia_cardiaca: data.frequencia_cardiaca }));

          setTelemetryHistory(prev => {
            const nextHistory = [...prev, data.frequencia_cardiaca];
            if (nextHistory.length > 15) nextHistory.shift();
            return nextHistory;
          });
        }
      } catch (err) {
        console.log('Erro de conexão ao buscar telemetria, caindo para simulação.');
      }
    };

    const startLocalSimulation = () => {
      setApiStatus('simulated');
      if (intervalRef.current) clearInterval(intervalRef.current);
      
      intervalRef.current = setInterval(() => {
        simTickRef.current += 1;
        
        // Simulação biométrica em repouso
        const baseFc = 72;
        const sinus = Math.sin(simTickRef.current * 0.4) * 4;
        const noise = (Math.random() * 2) - 1;
        const simFc = Math.round(baseFc + sinus + noise);

        const baseTemp = 36.4;
        const tempSinus = Math.sin(simTickRef.current * 0.2) * 0.15;
        const tempNoise = (Math.random() * 0.08) - 0.04;
        const simTemp = parseFloat((baseTemp + tempSinus + tempNoise).toFixed(1));

        const simulatedData = {
          temperatura: simTemp,
          frequencia_cardiaca: simFc,
          timestamp: new Date().toISOString(),
          alerta: false,
          mensagem_alerta: 'Sinais vitais normais.'
        };

        setTelemetry(simulatedData);
        setFormData(prev => ({ ...prev, frequencia_cardiaca: simFc }));

        setTelemetryHistory(prev => {
          const nextHistory = [...prev, simFc];
          if (nextHistory.length > 15) nextHistory.shift();
          return nextHistory;
        });
      }, 3000);
    };

    checkApiAndPoll();
    
    // Loop principal a cada 3 segundos
    const mainTimer = setInterval(() => {
      if (apiStatus === 'online') {
        fetchLatestTelemetry();
      } else {
        checkApiAndPoll();
      }
    }, 3000);

    return () => {
      clearInterval(mainTimer);
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [currentScreen, apiStatus]);

  // Lógica de Autenticação Simulada
  const handleLogin = () => {
    if (!email.includes('@') || password.length < 4) {
      setLoginError('Por favor, insira credenciais válidas.');
      return;
    }
    setLoginError('');
    setCurrentScreen('dashboard');
  };

  const handleLogout = () => {
    setCurrentScreen('login');
    setPredictionResult(null);
  };

  // Lógica de Cálculo de Risco Local (Fallback)
  const calcularScoreSimuladoLocal = (data) => {
    let score = 0.15; // Base de risco
    if (data.idade > 60) score += 0.25;
    else if (data.idade > 40) score += 0.10;

    if (data.frequencia_cardiaca > 90) score += 0.20;
    if (data.spo2 < 94) score += 0.25;
    if (data.historico_cardiaco === 1) score += 0.20;

    return Math.min(score, 0.98);
  };

  // Predição via Machine Learning
  const handlePredictML = async () => {
    setLoading(true);
    setLoadingType('ml');
    setErrorMsg('');
    setPredictionResult(null);

    if (apiStatus === 'simulated') {
      setTimeout(() => {
        const score = calcularScoreSimuladoLocal(formData);
        setPredictionResult({
          type: 'ml',
          probabilidade: `${(score * 100).toFixed(2)}%`,
          classificacao: score > 0.6 ? 'Alto Risco' : 'Baixo Risco',
          justificativa: `[Simulação Mobile]: Análise executada localmente. O paciente apresenta idade de ${formData.idade} anos, frequência cardíaca de ${formData.frequencia_cardiaca} bpm e saturação SpO2 de ${formData.spo2}%. Classificado como ${score > 0.6 ? 'Alto Risco' : 'Baixo Risco'} com base nos critérios simulados.`
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
      if (!response.ok) throw new Error('Servidor indisponível.');
      const data = await response.json();
      setPredictionResult({
        type: 'ml',
        probabilidade: data.probabilidade,
        classificacao: data.classificacao,
        justificativa: `[Modelo Random Forest]: Análise preditiva síncrona. Probabilidade calculada em ${data.probabilidade} para a combinação de idade (${formData.idade} anos), batimentos (${formData.frequencia_cardiaca} bpm), SpO2 (${formData.spo2}%) e histórico cardíaco (${formData.historico_cardiaco === 1 ? 'Sim' : 'Não'}).`
      });
    } catch (err) {
      setErrorMsg('Erro de conexão ao backend FastAPI. Executando fallback local.');
      const score = calcularScoreSimuladoLocal(formData);
      setPredictionResult({
        type: 'ml',
        probabilidade: `${(score * 100).toFixed(2)}%`,
        classificacao: score > 0.6 ? 'Alto Risco' : 'Baixo Risco',
        justificativa: `[Fallback Local]: Não foi possível conectar ao servidor. Simulação estimou risco de ${(score * 100).toFixed(2)}% (${score > 0.6 ? 'Alto Risco' : 'Baixo Risco'}) baseando-se nos parâmetros do paciente.`
      });
    } finally {
      setLoading(false);
    }
  };

  // Análise via Agentes Inteligentes
  const handleAnalyzeAgents = async () => {
    setLoading(true);
    setLoadingType('agent');
    setErrorMsg('');
    setPredictionResult(null);

    if (apiStatus === 'simulated') {
      setTimeout(() => {
        const score = calcularScoreSimuladoLocal(formData);
        setPredictionResult({
          type: 'agent',
          probabilidade: `${(score * 100).toFixed(2)}%`,
          classificacao: score > 0.6 ? 'Alto Risco' : 'Baixo Risco',
          agente: 'Agente Orquestrador CardioIA',
          protocolos: score > 0.6 
            ? ['Monitoramento contínuo em UTI.', 'Administração imediata de antiagregantes plaquetários.', 'Acionamento da equipe de hemodinâmica.']
            : ['Observação em enfermaria.', 'Realização de ECG seriado.', 'Avaliação cardiológica ambulatorial.'],
          justificativa: `[Simulação Multiagente]: O ecossistema de agentes determinou risco de ${(score * 100).toFixed(2)}%. Recomenda-se acompanhamento clínico adequado conforme os protocolos sugeridos pelo Especialista em Saúde.`
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
      if (!response.ok) throw new Error('Servidor retornou erro ou timeout.');
      const data = await response.json();
      setPredictionResult({
        type: 'agent',
        probabilidade: data.dados_analisados.probabilidade,
        classificacao: data.dados_analisados.classificacao,
        agente: data.agente_final,
        protocolos: data.dados_analisados.protocolos,
        justificativa: data.dados_analisados.justificativa
      });
    } catch (err) {
      setErrorMsg('Falha na resposta do servidor ou cota de IA excedida. Executando fallback.');
      const score = calcularScoreSimuladoLocal(formData);
      setPredictionResult({
        type: 'agent',
        probabilidade: `${(score * 100).toFixed(2)}%`,
        classificacao: score > 0.6 ? 'Alto Risco' : 'Baixo Risco',
        agente: 'Agente Orquestrador CardioIA (Fallback)',
        protocolos: score > 0.6 
          ? ['Monitoramento contínuo em UTI.', 'Administração imediata de antiagregantes plaquetários.', 'Acionamento da equipe de hemodinâmica.']
          : ['Observação em enfermaria.', 'Realização de ECG seriado.', 'Avaliação cardiológica ambulatorial.'],
        justificativa: `[Fallback Multiagente]: Ocorreu um erro no endpoint remoto (verifique a cota diária do Gemini no .env). Simulação local gerou parecer com ${(score * 100).toFixed(2)}% de probabilidade de risco clínico.`
      });
    } finally {
      setLoading(false);
    }
  };

  // Renderização da Tela de Login
  if (currentScreen === 'login') {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#0d0e12" />
        <View style={styles.loginWrapper}>
          <View style={styles.brandContainer}>
            <View style={styles.logoCircle}>
              <Heart size={44} color="#ff1744" fill="#ff1744" />
            </View>
            <Text style={styles.brandName}>CardioIA</Text>
            <Text style={styles.brandSlogan}>Coração Sob Controle</Text>
          </View>

          <View style={styles.formContainer}>
            <Text style={styles.loginTitle}>Área do Paciente</Text>
            
            {loginError ? <Text style={styles.errorText}>{loginError}</Text> : null}

            <View style={styles.inputContainer}>
              <User size={18} color="#6b7280" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="E-mail do Paciente"
                placeholderTextColor="#6b7280"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
              />
            </View>

            <View style={styles.inputContainer}>
              <Lock size={18} color="#6b7280" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="Senha de Acesso"
                placeholderTextColor="#6b7280"
                secureTextEntry
                value={password}
                onChangeText={setPassword}
              />
            </View>

            <TouchableOpacity style={styles.buttonLogin} onPress={handleLogin}>
              <Text style={styles.buttonLoginText}>Acessar Plataforma</Text>
            </TouchableOpacity>

            <Text style={styles.demoCredits}>Turma: 2TIAOR | Fase 7 MVP</Text>
          </View>
        </View>
      </SafeAreaView>
    );
  }

  // Renderização do Dashboard
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0d0e12" />
      
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerBrand}>
          <Heart size={22} color="#ff1744" fill="#ff1744" />
          <Text style={styles.headerTitle}>CardioIA</Text>
        </View>
        <View style={styles.headerActions}>
          <View style={[styles.apiBadge, apiStatus === 'online' ? styles.badgeOnline : styles.badgeSim]}>
            <View style={[styles.badgeDot, apiStatus === 'online' ? styles.dotOnline : styles.dotSim]} />
            <Text style={styles.badgeText}>{apiStatus === 'online' ? 'Servidor Ativo' : 'Simulado'}</Text>
          </View>
          <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
            <LogOut size={16} color="#ef4444" />
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Paciente Logado */}
        <View style={styles.patientBanner}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>BC</Text>
          </View>
          <View>
            <Text style={styles.patientName}>Bruno Conter</Text>
            <Text style={styles.patientSub}>RM 560518 • Monitoramento Ativo</Text>
          </View>
        </View>

        {/* Banner de Alerta Crítico */}
        {telemetry.alerta && (
          <View style={styles.alertBanner}>
            <AlertTriangle size={24} color="#ff1744" />
            <View style={styles.alertTextContainer}>
              <Text style={styles.alertTitle}>ALERTA DE SAÚDE</Text>
              <Text style={styles.alertMsg}>{telemetry.mensagem_alerta}</Text>
            </View>
          </View>
        )}

        {/* Painel IoT */}
        <Text style={styles.sectionTitle}>Sinais Vitais (Hardware IoT)</Text>
        <View style={styles.telemetryRow}>
          
          {/* Card Batimentos */}
          <View style={[styles.telemetryCard, telemetry.frequencia_cardiaca > 100 || telemetry.frequencia_cardiaca < 50 ? styles.cardDanger : null]}>
            <View style={styles.cardHeader}>
              <Activity size={16} color={telemetry.frequencia_cardiaca > 100 || telemetry.frequencia_cardiaca < 50 ? '#ff1744' : '#00e676'} />
              <Text style={styles.cardHeaderText}>Batimentos</Text>
            </View>
            <Text style={styles.cardValue}>{telemetry.frequencia_cardiaca} <Text style={styles.cardUnit}>BPM</Text></Text>
            <Text style={styles.cardStatus}>
              {telemetry.frequencia_cardiaca > 100 ? 'Taquicardia' : telemetry.frequencia_cardiaca < 50 ? 'Bradicardia' : 'Normal'}
            </Text>
          </View>

          {/* Card Temperatura */}
          <View style={[styles.telemetryCard, telemetry.temperatura > 38.0 || telemetry.temperatura < 35.0 ? styles.cardDanger : null]}>
            <View style={styles.cardHeader}>
              <Thermometer size={16} color={telemetry.temperatura > 38.0 || telemetry.temperatura < 35.0 ? '#ff1744' : '#00b0ff'} />
              <Text style={styles.cardHeaderText}>Temperatura</Text>
            </View>
            <Text style={styles.cardValue}>{telemetry.temperatura} <Text style={styles.cardUnit}>°C</Text></Text>
            <Text style={styles.cardStatus}>
              {telemetry.temperatura > 38.0 ? 'Febre' : telemetry.temperatura < 35.0 ? 'Hipotermia' : 'Normal'}
            </Text>
          </View>

        </View>

        {/* Evolução Gráfica Sparkline em Barras */}
        <View style={styles.chartPanel}>
          <View style={styles.chartHeader}>
            <TrendingUp size={16} color="#00b0ff" />
            <Text style={styles.chartTitle}>Frequência Cardíaca (Evolução)</Text>
          </View>
          
          <View style={styles.barChartContainer}>
            {telemetryHistory.map((fc, index) => {
              // Mapeia valor de 40 a 140 para altura percentual (20% a 95%)
              const percentage = Math.max(20, Math.min(95, ((fc - 40) / 100) * 100));
              const isDanger = fc > 100 || fc < 50;
              return (
                <View key={index} style={styles.barWrapper}>
                  <View style={[styles.bar, { height: `${percentage}%` }, isDanger ? styles.barDanger : styles.barNormal]} />
                </View>
              );
            })}
          </View>
          <View style={styles.chartFooter}>
            <Text style={styles.footerText}>Últimas 15 leituras em tempo real</Text>
            <Text style={styles.footerText}>Frequência Média: {Math.round(telemetryHistory.reduce((a,b)=>a+b, 0) / telemetryHistory.length)} BPM</Text>
          </View>
        </View>

        {/* Triagem e IA */}
        <Text style={styles.sectionTitle}>Triagem Médica e Predição</Text>
        
        <View style={styles.glassPanel}>
          <Text style={styles.panelInfo}>Os parâmetros abaixo são atualizados dinamicamente pela telemetria e serão usados na inferência preditiva da IA.</Text>
          
          {/* Inputs em Grid */}
          <View style={styles.formGrid}>
            <View style={styles.gridItem}>
              <Text style={styles.label}>Idade</Text>
              <TextInput
                style={styles.formInput}
                value={String(formData.idade)}
                keyboardType="numeric"
                onChangeText={text => setFormData(prev => ({ ...prev, idade: parseInt(text) || 0 }))}
              />
            </View>

            <View style={styles.gridItem}>
              <Text style={styles.label}>Batimentos (BPM)</Text>
              <TextInput
                style={[styles.formInput, { backgroundColor: '#1e202a', color: '#888' }]}
                value={String(formData.frequencia_cardiaca)}
                editable={false}
              />
            </View>

            <View style={styles.gridItem}>
              <Text style={styles.label}>SPO2 %</Text>
              <TextInput
                style={styles.formInput}
                value={String(formData.spo2)}
                keyboardType="numeric"
                onChangeText={text => setFormData(prev => ({ ...prev, spo2: parseInt(text) || 0 }))}
              />
            </View>

            <View style={styles.gridItem}>
              <Text style={styles.label}>Histórico Cardíaco</Text>
              <View style={styles.toggleRow}>
                <TouchableOpacity 
                  style={[styles.toggleBtn, formData.historico_cardiaco === 0 ? styles.toggleActive : null]}
                  onPress={() => setFormData(prev => ({ ...prev, historico_cardiaco: 0 }))}
                >
                  <Text style={[styles.toggleText, formData.historico_cardiaco === 0 ? styles.toggleTextActive : null]}>Não</Text>
                </TouchableOpacity>
                <TouchableOpacity 
                  style={[styles.toggleBtn, formData.historico_cardiaco === 1 ? styles.toggleActive : null]}
                  onPress={() => setFormData(prev => ({ ...prev, historico_cardiaco: 1 }))}
                >
                  <Text style={[styles.toggleText, formData.historico_cardiaco === 1 ? styles.toggleTextActive : null]}>Sim</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>

          {/* Botões de Ação */}
          <View style={styles.actionRow}>
            <TouchableOpacity style={styles.actionBtnML} onPress={handlePredictML} disabled={loading}>
              <Sliders size={16} color="#fff" />
              <Text style={styles.actionBtnText}>Análise ML (Rápida)</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionBtnAgent} onPress={handleAnalyzeAgents} disabled={loading}>
              <Cpu size={16} color="#fff" />
              <Text style={styles.actionBtnText}>Agentes (Completa)</Text>
            </TouchableOpacity>
          </View>

          {loading && (
            <View style={styles.loaderContainer}>
              <ActivityIndicator size="small" color="#00b0ff" />
              <Text style={styles.loaderText}>
                {loadingType === 'ml' ? 'Executando inferência pelo modelo Random Forest...' : 'Orquestrando sistema de agentes CardioIA (Gemini)...'}
              </Text>
            </View>
          )}

          {errorMsg ? (
            <View style={styles.errorBanner}>
              <Text style={styles.errorBannerText}>{errorMsg}</Text>
            </View>
          ) : null}
        </View>

        {/* Resultados da IA */}
        {predictionResult && (
          <View style={styles.resultContainer}>
            <Text style={styles.resultHeading}>Parecer de IA Gerado</Text>
            
            <View style={styles.resultHeader}>
              <View>
                <Text style={styles.resultLabel}>Probabilidade de Risco</Text>
                <Text style={styles.resultProb}>{predictionResult.probabilidade}</Text>
              </View>
              <View style={[styles.riskBadge, predictionResult.classificacao.includes('Alto') ? styles.riskBadgeHigh : styles.riskBadgeLow]}>
                <Text style={[styles.riskBadgeText, predictionResult.classificacao.includes('Alto') ? styles.riskTextHigh : styles.riskTextLow]}>
                  {predictionResult.classificacao}
                </Text>
              </View>
            </View>

            {predictionResult.agente && (
              <Text style={styles.resultAgent}>Agente Responsável: <Text style={{ color: '#00b0ff', fontWeight: 'bold' }}>{predictionResult.agente}</Text></Text>
            )}

            {predictionResult.protocolos && (
              <View style={styles.protocolContainer}>
                <Text style={styles.protocolTitle}>Protocolos Clínicos Recomendados:</Text>
                {predictionResult.protocolos.map((p, idx) => (
                  <View key={idx} style={styles.protocolItem}>
                    <CheckCircle2 size={14} color="#00e676" style={{ marginRight: 6, marginTop: 2 }} />
                    <Text style={styles.protocolText}>{p}</Text>
                  </View>
                ))}
              </View>
            )}

            <View style={styles.justContainer}>
              <Text style={styles.justTitle}>Justificativa e Análise Clínica:</Text>
              <Text style={styles.justText}>{predictionResult.justificativa}</Text>
            </View>
          </View>
        )}
        
        {/* Espaço no final para rolagem suave */}
        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0d0e12',
  },
  // LOGIN STYLE
  loginWrapper: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: 24,
  },
  brandContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logoCircle: {
    width: 90,
    height: 90,
    borderRadius: 45,
    backgroundColor: 'rgba(255, 23, 68, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    borderWidth: 1.5,
    borderColor: 'rgba(255, 23, 68, 0.4)',
  },
  brandName: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    letterSpacing: 1,
  },
  brandSlogan: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 4,
  },
  formContainer: {
    backgroundColor: '#161822',
    borderRadius: 16,
    padding: 24,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.3,
    shadowRadius: 20,
    elevation: 8,
  },
  loginTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 20,
    textAlign: 'center',
  },
  errorText: {
    color: '#ff1744',
    fontSize: 13,
    marginBottom: 12,
    textAlign: 'center',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0d0e12',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 10,
    marginBottom: 16,
    paddingHorizontal: 12,
    height: 48,
  },
  inputIcon: {
    marginRight: 10,
  },
  input: {
    flex: 1,
    color: '#fff',
    fontSize: 15,
  },
  buttonLogin: {
    backgroundColor: '#ff1744',
    borderRadius: 10,
    height: 48,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 8,
    shadowColor: '#ff1744',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 4,
  },
  buttonLoginText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  demoCredits: {
    textAlign: 'center',
    fontSize: 12,
    color: '#4b5563',
    marginTop: 20,
  },

  // DASHBOARD STYLE
  header: {
    height: 60,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
    backgroundColor: '#161822',
  },
  headerBrand: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginLeft: 6,
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  apiBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 20,
    borderWidth: 1,
  },
  badgeOnline: {
    backgroundColor: 'rgba(0, 230, 118, 0.05)',
    borderColor: 'rgba(0, 230, 118, 0.3)',
  },
  badgeSim: {
    backgroundColor: 'rgba(0, 176, 255, 0.05)',
    borderColor: 'rgba(0, 176, 255, 0.3)',
  },
  badgeDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginRight: 6,
  },
  dotOnline: {
    backgroundColor: '#00e676',
  },
  dotSim: {
    backgroundColor: '#00b0ff',
  },
  badgeText: {
    fontSize: 11,
    color: '#fff',
    fontWeight: '600',
  },
  logoutBtn: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  scrollContent: {
    padding: 16,
  },
  patientBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#161822',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
    marginBottom: 16,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#ff1744',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  avatarText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  patientName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  patientSub: {
    color: '#6b7280',
    fontSize: 12,
    marginTop: 2,
  },
  alertBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 23, 68, 0.1)',
    borderWidth: 1.5,
    borderColor: '#ff1744',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    gap: 12,
  },
  alertTextContainer: {
    flex: 1,
  },
  alertTitle: {
    color: '#ff1744',
    fontWeight: 'bold',
    fontSize: 14,
  },
  alertMsg: {
    color: '#fff',
    fontSize: 13,
    marginTop: 2,
  },
  sectionTitle: {
    color: '#9ca3af',
    fontSize: 14,
    fontWeight: 'bold',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 10,
    marginTop: 8,
  },
  telemetryRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  telemetryCard: {
    flex: 1,
    backgroundColor: '#161822',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
  },
  cardDanger: {
    borderColor: '#ff1744',
    borderWidth: 1.5,
    backgroundColor: 'rgba(255, 23, 68, 0.02)',
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 8,
  },
  cardHeaderText: {
    color: '#9ca3af',
    fontSize: 12,
    marginLeft: 4,
  },
  cardValue: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  cardUnit: {
    fontSize: 13,
    color: '#9ca3af',
    fontWeight: 'normal',
  },
  cardStatus: {
    color: '#9ca3af',
    fontSize: 12,
    marginTop: 6,
  },

  // Sparkline Chart
  chartPanel: {
    backgroundColor: '#161822',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
    marginBottom: 16,
  },
  chartHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 16,
  },
  chartTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  barChartContainer: {
    height: 80,
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'space-between',
    paddingHorizontal: 4,
    marginBottom: 12,
  },
  barWrapper: {
    flex: 1,
    height: '100%',
    justifyContent: 'flex-end',
    alignItems: 'center',
    paddingHorizontal: 1,
  },
  bar: {
    width: '80%',
    borderRadius: 2,
  },
  barNormal: {
    backgroundColor: '#00b0ff',
  },
  barDanger: {
    backgroundColor: '#ff1744',
  },
  chartFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    borderTopWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
    paddingTop: 8,
  },
  footerText: {
    fontSize: 11,
    color: '#6b7280',
  },

  // Triagem Form
  glassPanel: {
    backgroundColor: '#161822',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
    marginBottom: 16,
  },
  panelInfo: {
    color: '#9ca3af',
    fontSize: 12,
    lineHeight: 16,
    marginBottom: 16,
  },
  formGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  gridItem: {
    width: '47%',
    marginBottom: 12,
  },
  label: {
    color: '#9ca3af',
    fontSize: 12,
    marginBottom: 6,
  },
  formInput: {
    backgroundColor: '#0d0e12',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 8,
    height: 40,
    paddingHorizontal: 10,
    color: '#fff',
    fontSize: 14,
  },
  toggleRow: {
    flexDirection: 'row',
    backgroundColor: '#0d0e12',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    height: 40,
    padding: 2,
  },
  toggleBtn: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 6,
  },
  toggleActive: {
    backgroundColor: '#1f2937',
  },
  toggleText: {
    color: '#6b7280',
    fontSize: 13,
  },
  toggleTextActive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  actionRow: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 12,
  },
  actionBtnML: {
    flex: 1,
    backgroundColor: '#1f2937',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 8,
    height: 42,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
  },
  actionBtnAgent: {
    flex: 1,
    backgroundColor: '#00b0ff',
    borderRadius: 8,
    height: 42,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
  },
  actionBtnText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: 'bold',
  },
  loaderContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginTop: 16,
    backgroundColor: 'rgba(0, 176, 255, 0.03)',
    padding: 10,
    borderRadius: 8,
    borderWidth: 0.5,
    borderColor: 'rgba(0, 176, 255, 0.2)',
  },
  loaderText: {
    color: '#00b0ff',
    fontSize: 11,
    flex: 1,
  },
  errorBanner: {
    marginTop: 12,
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    padding: 10,
    borderRadius: 8,
    borderWidth: 0.5,
    borderColor: '#ef4444',
  },
  errorBannerText: {
    color: '#ef4444',
    fontSize: 12,
  },

  // Resultados
  resultContainer: {
    backgroundColor: '#161822',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1.5,
    borderColor: '#00b0ff',
    marginBottom: 24,
    shadowColor: '#00b0ff',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 6,
  },
  resultHeading: {
    color: '#fff',
    fontSize: 15,
    fontWeight: 'bold',
    marginBottom: 14,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
    paddingBottom: 12,
    marginBottom: 12,
  },
  resultLabel: {
    color: '#9ca3af',
    fontSize: 11,
  },
  resultProb: {
    color: '#fff',
    fontSize: 28,
    fontWeight: 'bold',
    marginTop: 2,
  },
  riskBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  riskBadgeHigh: {
    backgroundColor: 'rgba(255, 23, 68, 0.1)',
  },
  riskBadgeLow: {
    backgroundColor: 'rgba(0, 230, 118, 0.1)',
  },
  riskBadgeText: {
    fontSize: 13,
    fontWeight: 'bold',
  },
  riskTextHigh: {
    color: '#ff1744',
  },
  riskTextLow: {
    color: '#00e676',
  },
  resultAgent: {
    color: '#9ca3af',
    fontSize: 12,
    marginBottom: 12,
  },
  protocolContainer: {
    backgroundColor: '#0d0e12',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  protocolTitle: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  protocolItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 6,
  },
  protocolText: {
    color: '#d1d5db',
    fontSize: 12,
    flex: 1,
    lineHeight: 16,
  },
  justContainer: {
    backgroundColor: '#0d0e12',
    borderRadius: 8,
    padding: 12,
  },
  justTitle: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 6,
  },
  justText: {
    color: '#d1d5db',
    fontSize: 12,
    lineHeight: 18,
    textAlign: 'justify',
  }
});
