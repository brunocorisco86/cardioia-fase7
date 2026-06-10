# 📋 Avaliação de Completude e Roadmap: CardioIA (Fase 7)

Este documento apresenta a análise de completude do repositório atual em relação aos requisitos obrigatórios do enunciado da **Fase 7 - CardioIA (Coração Sob Controle: Previsão de Crises com IA)** e define o roadmap de implementação para o desenvolvimento do MVP final, desconsiderando os tópicos opcionais "Ir Além".

---

## 📊 1. Avaliação de Completude do Repositório

Atualmente, o repositório contém o código do projeto **ORBITAL-IA** (monitoramento de detritos espaciais). Por se tratar de um escopo totalmente distinto do projeto da **CardioIA**, a completude das metas obrigatórias da Fase 7 é de **0%**. 

Abaixo está o detalhamento dos requisitos obrigatórios comparados com o estado atual:

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

---

## 🗺️ 2. Roadmap de Implementação Proposto

Para guiar o desenvolvimento completo dos entregáveis obrigatórios da **CardioIA**, o projeto foi estruturado em 5 etapas principais:

### 📂 Etapa 1: Estruturação do Repositório (Limpeza e Arquitetura de Pastas)
- [ ] Criar a estrutura física de diretórios para segmentar responsabilidades:
  - `/backend` - API Python (FastAPI/Flask) + Modelos de IA
  - `/frontend-web` - SPA React + Vite
  - `/mobile-app` - React Native + Expo
  - `/iot` - Código MicroPython e esquemáticos
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

### 📝 Etapa 5: Documentação Final, Diagrama e Vídeo
- [ ] **Diagrama de Arquitetura:** Desenhar a arquitetura de ponta a ponta (Sensor -> MicroPython -> API Backend -> IA Modelos/LLM -> Web/Mobile) e salvar em `docs/arquitetura_final.png`.
- [ ] **Relatório Técnico em PDF:** Redigir o relatório técnico obrigatório (máximo de 5 páginas) e salvar em `docs/`.
- [ ] **Vídeo de Demonstração:** Gravar uma demonstração em vídeo (até 5 minutos) evidenciando a simulação no Wokwi alterando os dados de saúde, a chamada na API de Backend gerando a predição, e os dashboards web/mobile se atualizando em tempo real.
- [ ] **Atualização do README:** Consolidar todas as informações no `README.md` principal do repositório, incluindo os links de deploy Vercel, link de download do APK e link de acesso ao Wokwi.
