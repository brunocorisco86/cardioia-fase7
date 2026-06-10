# 📋 Avaliação de Completude e Roadmap: CardioIA (Fase 7)

> ### 📊 Status de Completude Geral: **50%**
> `[████████████████████░░░░░░░░░░░░░░░░░░░░]` **(3.5/7 requisitos concluídos)**

Este documento apresenta a análise de completude do repositório atual em relação aos requisitos obrigatórios do enunciado da **Fase 7 - CardioIA (Coração Sob Controle: Previsão de Crises com IA)** e define o roadmap de implementação para o desenvolvimento do MVP final, desconsiderando os tópicos opcionais "Ir Além".

> 💡 **Atualização Recente:** O repositório foi limpo e integrado com o conteúdo oficial da **Fase 6 da CardioIA** (modelo de ML `modelo_cardioia.pkl` e orquestração de agentes `cardioia_agents.py` via OpenAI Agents SDK). Com isso, a fundação algorítmica de IA está pronta, elevando a completude geral para **15%**.

---

## 📊 1. Avaliação de Completude do Repositório

Abaixo está o detalhamento dos requisitos obrigatórios comparados com o estado atual dos arquivos na raiz:

### PARTE 1 – Deploy e Distribuição Profissional (Front-End & Mobile)
| Requisito do Enunciado | Estado Atual | Completude | Pendências |
| :--- | :--- | :---: | :--- |
| **Web SPA (React + Vite)** publicada na Vercel com suporte a rotas configuradas via `vercel.json` e CI/CD ativo. | A aplicação SPA em React + Vite está implementada em `frontend-web/` com layout premium, gráficos e `vercel.json`. | **100%** | Nenhuma (CI/CD ativo ao conectar o repositório). |
| **Mobile (React Native + Expo)** configurado com `app.json` (android package em domínio invertido) e `eas.json` (perfil preview). | Não há pasta ou código de aplicativo mobile. | **0%** | Estruturar o app React Native, configurar `app.json`/`eas.json` e rodar o build no Expo. |
| **README.md** com URL pública da Vercel, link/QR Code para o APK, prints comprobatórios de deploy e instruções. | O `README.md` foi atualizado com a ementa da CardioIA e os integrantes, mas carece de links finais. | **20%** | Inserir as URLs públicas da Vercel, links do build no Expo e prints comprobatórios da Fase 7. |

### PARTE 2 – Integração do Ecossistema e Arquitetura Final
| Requisito do Enunciado | Estado Atual | Completude | Pendências |
| :--- | :--- | :---: | :--- |
| **Back-end Integrador (Python)** conectando as interfaces (Front-end) aos motores de IA (Fase 6) e LLMs (Fase 5). | O servidor API (FastAPI) está implementado em `backend/app.py` integrando modelo ML, sistema de agentes e recepção de telemetria. | **100%** | Nenhuma. |
| **Transição para MicroPython** da lógica de sensores (temperatura e batimentos cardíacos simulados) na pasta `IoT`. | O script de firmware compatível com MicroPython está desenvolvido em `iot/main.py`. | **100%** | Nenhuma. |
| **Projeto Wokwi** (link público da simulação em MicroPython demonstrando a leitura e alertas com LED/OLED). | Não há referências a simulação IoT ou link do Wokwi. | **0%** | Montar a simulação no Wokwi e obter o link do projeto compartilhado. |
| **Relatório Técnico (PDF)** de até 5 páginas com Diagrama de Arquitetura Final (fluxo fim-a-fim) e link do vídeo de 5 min. | Existem os relatórios PDF da Fase 6. | **0% (Fase 7)** | Modelar o diagrama técnico da arquitetura integrada da Fase 7, produzir o PDF e gravar o vídeo. |

---

## 🗺️ 2. Roadmap de Implementação Proposto

Para guiar o desenvolvimento completo dos entregáveis obrigatórios da **CardioIA**, o projeto foi estruturado em 5 etapas principais:

### 📂 Etapa 1: Estruturação do Repositório (Limpeza e Arquitetura de Pastas)
- [x] Mover os arquivos e códigos da Fase 6 para a pasta `/backend` para segmentar responsabilidades.
- [x] Criar a estrutura física de diretórios básicos:
  - [x] `/backend` - API Python + Motores de IA (OpenAI Agents SDK)
  - [x] `/iot` - Pasta reservada para MicroPython e esquemáticos
  - [x] `/docs` - Enunciados, Diagramas e Relatórios Técnicos
  - [x] `/entregaveis` - Pasta de entregáveis com link do GitHub configurado
  - [x] `/frontend-web` - SPA React + Vite (A ser inicializada)
  - [ ] `/mobile-app` - React Native + Expo (A ser inicializada)

### 🧠 Etapa 2: Backend Integrador e Modelos de IA
- [x] **Configuração da API:** Inicializar um servidor FastAPI na pasta `backend/` com rotas para receber telemetria dos sensores e servir as interfaces.
- [x] **Integração do Modelo Preditivo:** Adaptar o `cardioia_evaluation.py` para rodar como ferramenta exposta na API da CardioIA.
- [x] **Adaptação dos Agentes:** Exportar o Runner do `cardioia_agents.py` para processar chamadas dinâmicas a partir de requisições do front-end.

### 🔌 Etapa 3: Hardware, MicroPython e Simulação IoT
- [x] **Lógica do Dispositivo:** Desenvolver em `iot/main.py` o script compatível com MicroPython para rodar no Raspberry Pi Pico W ou ESP32.
- [x] **Captura de Sinais:** Escrever a lógica de leitura simulada dos sensores de temperatura e batimentos cardíacos.
- [ ] **Simulação no Wokwi:** Montar a placa com leitor de temperatura (ex: DHT22), potenciômetro (simulando batimentos), display OLED (para feedbacks locais) e leds/buzzer de alerta.
- [x] **Conexão:** Habilitar o MicroPython para enviar os sinais lidos via HTTP POST ao endpoint da nossa API de Backend.

### 🌐 Etapa 4: Interfaces Web, Mobile e Pipeline de Deploy
- [x] **Desenvolvimento Web (React + Vite):**
  - [x] Desenvolver o dashboard médico atualizado com gráficos em tempo real e lista de pacientes monitorados.
  - [x] Implementar alertas visuais em caso de risco clínico elevado.
  - [x] Criar o arquivo `vercel.json` configurado para redirecionamento SPA e conectar o repositório ao deploy automático da Vercel.
- [ ] **Desenvolvimento Mobile (React Native + Expo):**
  - Implementar tela de login e visualização dos batimentos/temperatura do próprio paciente.
  - Criar `app.json` (definindo o package Android) e `eas.json` (perfil preview).
  - Executar o build na nuvem via Expo CLI (`eas build --platform android --profile preview`) para obter o arquivo `.apk`.

### 📝 Etapa 5: Documentação Final, Diagrama e Vídeo
- [ ] **Diagrama de Arquitetura:** Desenhar a arquitetura de ponta a ponta (Sensor -> MicroPython -> API Backend -> IA Modelos/LLM -> Web/Mobile) e salvar em `docs/arquitetura_final.png`.
- [ ] **Relatório Técnico em PDF:** Redigir o relatório técnico obrigatório da Fase 7 (máximo de 5 páginas) e salvar em `docs/`.
- [ ] **Vídeo de Demonstração:** Gravar uma demonstração em vídeo (até 5 minutos) evidenciando a simulação no Wokwi alterando os dados de saúde, a chamada na API de Backend gerando a predição, e os dashboards web/mobile se atualizando em tempo real.
- [ ] **Atualização do README:** Consolidar todas as informações no `README.md` principal do repositório, incluindo os links de deploy Vercel, link de download do APK e link de acesso ao Wokwi.
