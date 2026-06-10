# 📋 Avaliação de Completude e Roadmap: CardioIA (Fase 7)

Este documento apresenta a análise de completude do repositório atual em relação aos requisitos do enunciado da **Fase 7 - CardioIA (Coração Sob Controle: Previsão de Crises com IA)** e define o roadmap detalhado de implementação para o desenvolvimento do MVP final.

---

## 📊 1. Avaliação de Completude do Repositório

Atualmente, o repositório contém a base do projeto **ORBITAL-IA** (voltado ao monitoramento de detritos espaciais e previsão de colisões orbitais). Por se tratar de um tema e código distintos do escopo da **CardioIA**, a taxa de completude geral para a entrega exigida é de **0%**. 

Abaixo está o detalhamento item a item confrontando as exigências do enunciado com o estado atual:

### PARTE 1 – Deploy e Distribuição Profissional (Front-End & Mobile)
| Requisito do Enunciado | Estado Atual | Completude | Pendências |
| :--- | :--- | :---: | :--- |
| **Web SPA (React + Vite)** publicada na Vercel com suporte a rotas configuradas via `vercel.json` e CI/CD ativo. | Não há pasta ou código de front-end. | **0%** | Criar o front-end, configurar o `vercel.json` e conectar com a Vercel. |
| **Mobile (React Native + Expo)** configurado com `app.json` (android package em domínio invertido) e `eas.json` (perfil preview). | Não há pasta ou código de aplicativo mobile. | **0%** | Estruturar o app React Native, configurar `app.json`/`eas.json` e rodar o build no Expo. |
| **README.md** com URL pública da Vercel, link/QR Code para o APK, prints comprobatórios de deploy e instruções. | O `README.md` atual descreve o projeto ORBITAL-IA. | **0%** | Reescrever o README focando no projeto CardioIA e inserindo os links da entrega. |

### PARTE 2 – Integração do Ecossistema e Arquitetura Final
| Requisito do Enunciado | Estado Atual | Completude | Pendências |
| :--- | :--- | :---: | :--- |
| **Back-end Integrador (Python)** conectando as interfaces (Front-end) aos motores de IA (Fase 6) e LLMs (Fase 5). | Existem scripts Python locais para o Orbital-IA, sem servidor HTTP ou endpoints clínicos. | **0%** | Desenvolver uma API em Python (FastAPI/Flask) integrando os modelos de risco cardíaco e APIs de LLM. |
| **Transição para MicroPython** da lógica de sensores (temperatura e batimentos cardíacos simulados) na pasta `IoT`. | Não há pasta `IoT` ou scripts MicroPython no repositório. | **0%** | Escrever a lógica em MicroPython e criar o script `.py` dedicado na pasta `IoT`. |
| **Projeto Wokwi** (link público da simulação em MicroPython demonstrando a leitura e alertas com LED/OLED). | Não há referências a simulação IoT ou link do Wokwi. | **0%** | Montar a simulação no Wokwi e obter o link do projeto compartilhado. |
| **Relatório Técnico (PDF)** de até 5 páginas com Diagrama de Arquitetura Final (fluxo fim-a-fim) e link do vídeo de 5 min. | Arquivo não existente. | **0%** | Modelar o diagrama técnico de arquitetura, produzir o relatório e gravar a demonstração em vídeo. |

### IR ALÉM 1 – Mineração de Processos e Conformidade Clínica (AIRPA)
| Requisito do Enunciado | Estado Atual | Completude | Pendências |
| :--- | :--- | :---: | :--- |
| **Notebook Python (pm4py)** processando logs de eventos de IAM, detectando variantes, gargalos e tempo de ciclo. | Não há notebooks ou conjuntos de dados de mineração de processos. | **0%** | Criar o notebook implementando a biblioteca `pm4py` com logs de evento de infarto (IAM). |
| **Relatório Técnico (PDF 2 páginas)** explicando as variantes clínicas e os impactos de conformidade detectados. | Não há relatório específico sobre mineração de processos. | **0%** | Elaborar o relatório técnico de processos baseado nos resultados gerados no notebook. |

### IR ALÉM 2 – Recuperação de Casos com Embeddings Visuais (CBIR)
| Requisito do Enunciado | Estado Atual | Completude | Pendências |
| :--- | :--- | :---: | :--- |
| **Notebook Google Colab** implementando pipeline CBIR para busca de similaridade em radiografias de tórax e Precision@K. | Não há notebooks de visão computacional voltados à recuperação de imagens médicas por similaridade. | **0%** | Construir o notebook de extração de embeddings, indexação vetorial e cálculo de Precision@K. |
| **Relatório Técnico (PDF 2 páginas)** com resultados visuais da busca, análise qualitativa e limitações do modelo. | Arquivo não existente. | **0%** | Escrever a análise de vizinhos próximos e limitações do modelo de embeddings visuais. |

---

## 🗺️ 2. Roadmap de Implementação Proposto

Para guiar a transição e o desenvolvimento completo do ecossistema **CardioIA**, sugere-se a divisão do projeto nas 6 etapas abaixo:

### 📂 Etapa 1: Estruturação do Repositório (Limpeza e Arquitetura de Pastas)
- [ ] Criar a estrutura física de diretórios para segmentar responsabilidades:
  - `/backend` - API Python (FastAPI/Flask) + Modelos de IA
  - `/frontend-web` - SPA React + Vite
  - `/mobile-app` - React Native + Expo
  - `/iot` - Código MicroPython e esquemáticos
  - `/analytics` - Notebooks das seções 'Ir Além' (Process Mining e CBIR)
  - `/docs` - Enunciados, Diagramas e Relatórios Técnicos

### 🧠 Etapa 2: Backend Integrador e Modelos de IA
- [ ] **Configuração da API:** Inicializar um servidor FastAPI na pasta `backend/` com rotas para receber telemetria dos sensores e servir as interfaces.
- [ ] **Integração do Modelo Preditivo:** Importar o modelo classificador de risco cardíaco (Fase 6) para calcular a probabilidade de crise clínica baseada em batimentos e temperatura.
- [ ] **Integração com LLM (Fase 5):** Configurar um client para a API da OpenAI/Anthropic/Gemini para gerar recomendações médicas e explicações em linguagem natural com base no nível de risco predito.

### 🔌 Etapa 3: Hardware, MicroPython e Simulação IoT
- [ ] **Lógica do Dispositivo:** Desenvolver em `iot/main.py` o script compatível com MicroPython para rodar no Raspberry Pi Pico W ou ESP32.
- [ ] **Captura de Sinais:** Escrever a lógica de leitura simulada dos sensores de temperatura e batimentos cardíacos.
- [ ] **Simulação no Wokwi:** Montar a placa com leitor de temperatura (ex: DHT22), potenciômetro (simulando batimentos), display OLED (para feedbacks locais) e leds/buzzer de alerta.
- [ ] **Conexão:** Habilitar o MicroPython para enviar os sinais lidos via HTTP POST ao endpoint da nossa API de Backend local ou em nuvem.

### 🌐 Etapa 4: Interfaces Web, Mobile e Pipeline de Deploy
- [ ] **Desenvolvimento Web (React + Vite):**
  - Desenvolver o dashboard médico atualizado com gráficos em tempo real e lista de pacientes monitorados.
  - Implementar alertas visuais em caso de risco clínico elevado.
  - Criar o arquivo `vercel.json` configurado para redirecionamento SPA e conectar o repositório ao deploy automático da Vercel.
- [ ] **Desenvolvimento Mobile (React Native + Expo):**
  - Implementar tela de login e visualização dos batimentos/temperatura do próprio paciente.
  - Criar `app.json` (definindo o package Android) e `eas.json` (perfil preview).
  - Executar o build na nuvem via Expo CLI (`eas build --platform android --profile preview`) para obter o arquivo `.apk`.

### 📊 Etapa 5: Implementação dos Módulos "Ir Além" (AIRPA & CBIR)
- [ ] **Mineração de Processos (AIRPA):**
  - Gerar ou estruturar um arquivo CSV/event log simulando o protocolo de atendimento de Infarto Agudo do Miocárdio (IAM).
  - Implementar um Jupyter Notebook em `analytics/process_mining.ipynb` aplicando a biblioteca `pm4py`.
  - Gerar gráficos de variantes de fluxo (Heuristics Net, Petri Net) e realizar a análise de conformidade clínica.
- [ ] **Recuperação de Casos por Imagem (CBIR):**
  - Criar o notebook `analytics/cbir_chest_xray.ipynb`.
  - Configurar a extração de embeddings visuais de radiografias de tórax usando um modelo de visão computacional pré-treinado (ex: ResNet50 ou MobileNetV2).
  - Indexar embeddings e programar a busca por similaridade de cosseno, avaliando o algoritmo com a métrica Precision@K.

### 📝 Etapa 6: Documentação Final, Diagrama e Vídeo
- [ ] **Diagrama de Arquitetura:** Desenhar a arquitetura de ponta a ponta (Sensor -> MicroPython -> API Backend -> IA Modelos/LLM -> Web/Mobile) e salvar em `docs/arquitetura_final.png`.
- [ ] **Relatórios em PDF:** Redigir os relatórios técnicos obrigatórios (Geral, AIRPA e CBIR) e salvar em `docs/`.
- [ ] **Vídeo de Demonstração:** Gravar uma demonstração em vídeo (até 5 minutos) evidenciando a simulação no Wokwi alterando os dados de saúde, a chamada na API de Backend gerando a predição, e os dashboards web/mobile se atualizando em tempo real.
- [ ] **Atualização do README:** Consolidar todas as informações no `README.md` principal do repositório, incluindo os links de deploy Vercel, link de download do APK e link de acesso ao Wokwi.
