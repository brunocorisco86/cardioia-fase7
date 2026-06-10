# 🗺️ Plano de Implementação: Frontend Web SPA (React + Vite)

Este documento detalha o plano de ação para a implementação da **Interface Web SPA** (Etapa 4 do Roadmap) do projeto CardioIA.

## 🎯 Objetivos
Desenvolver um painel de controle (Dashboard) médico de alta fidelidade visual (premium dark mode) que consumirá os dados da nossa API FastAPI em tempo real, permitindo:
1. **Monitoramento IoT em Tempo Real:** Visualização dinâmica de batimentos cardíacos (bpm) e temperatura corporal (°C) com gráficos interativos.
2. **Visualização de Alertas Críticos:** Sistema de notificações visuais imediatas acionadas por anomalias nos sinais vitais do paciente.
3. **Análise Preditiva e Multiagente:** Painel interativo para entrada de dados do paciente e visualização de previsões de Machine Learning e relatórios multiagente em markdown.
4. **Deploy Facilitado:** Configuração do `vercel.json` para publicação contínua na Vercel com suporte a rotas SPA.

---

## 🛠️ Escopo da Implementação

### 1. Inicialização do Projeto
*   Utilizar Vite com React para criar uma estrutura SPA otimizada em `/frontend-web`.
*   Estruturar as pastas: `/components`, `/hooks`, `/services`, `/styles`.

### 2. Estilização Premium (Vanilla CSS)
*   Seguindo as diretrizes estéticas: dark mode minimalista, bordas arredondadas suaves, efeitos de vidro (glassmorphism), fontes modernas (Outfit/Inter) e transições fluidas.
*   Paleta de cores moderna: pretos e cinzas profundos para o background, azul néon para dados normais, verde esmeralda para conformidade e vermelho rubi/coral para alertas.

### 3. Integração com a API
*   Criação de serviços de chamada à API utilizando `fetch` (ou similar) conectando com:
    *   `GET /api/telemetry/latest` para atualização em tempo real de temperatura e batimentos cardíacos.
    *   `POST /api/predict` para a estimativa imediata de risco cardíaco.
    *   `POST /api/analyze` para a consulta aos agentes especialistas e orquestrador.

### 4. Componentes Principais
*   `Sidebar / Navigation`: Navegação intuitiva no painel.
*   `TelemetryCard`: Exibição numérica e status da temperatura e batimentos, mudando de cor dinamicamente em caso de alerta.
*   `RealTimeChart`: Gráfico de linha interativo exibindo a evolução temporal dos sinais vitais.
*   `PredictiveForm`: Formulário interativo para entrada dos dados do paciente e acionamento da análise.
*   `AgentReport`: Exibição estilizada do parecer médico final gerado pela orquestração de agentes.

### 5. Configurações de Build e Deploy
*   Criação de `vercel.json` para resolver problemas de rotas SPA no deploy da Vercel.

---

## 📋 Próximos Passos
1. **Aprovação do Plano:** Iniciar a criação da aplicação SPA.
2. **Setup do Vite:** Criar o projeto via CLI em `/frontend-web`.
3. **Codificação:** Escrever estilos, hooks e componentes.
4. **Testes do Frontend:** Executar e testar a comunicação com a API.
5. **Sincronização:** Commit, atualização do roadmap e push.
