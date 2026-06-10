# 🗺️ Plano de Implementação: Backend Integrador (FastAPI)

Este documento detalha o plano de ação para a implementação da **Etapa 2: Backend Integrador e Modelos de IA** do projeto CardioIA.

## 🎯 Por que iniciar pelo Backend?
O Backend Integrador é o pilar central que conecta todas as partes do ecossistema:
1. **IoT / MicroPython:** Enviará dados de telemetria em tempo real.
2. **Modelo de ML:** Fornecerá predições rápidas de risco cardíaco.
3. **Agentes Inteligentes (LLM):** Executará o raciocínio complexo e a geração de relatórios de conformidade baseados em protocolos médicos.
4. **Web / Mobile:** Exibirá painéis de controle atualizados em tempo real com as informações da API.

---

## 🛠️ Escopo da Implementação

### 1. Novo Servidor FastAPI (`backend/app.py`)
Criaremos o arquivo principal do servidor, com as seguintes funcionalidades:
*   **Configuração de CORS:** Permitir requisições de origens variadas (importante para Web SPA na Vercel e Mobile).
*   **Rotas da API:**
    *   `GET /`: Health check da API.
    *   `POST /api/predict`: Executa a predição rápida usando o arquivo `modelo_cardioia.pkl` diretamente.
    *   `POST /api/analyze`: Executa o fluxo completo do sistema multiagente do `cardioia_agents.py` com o Gemini, retornando a resposta estruturada.
    *   `POST /api/telemetry`: Endpoint para o dispositivo IoT (ESP32/Pico W com MicroPython) enviar os sinais vitais coletados (temperatura, batimentos cardíacos). Armazenará o estado temporário na memória para o painel em tempo real consultar.
    *   `GET /api/telemetry/latest`: Rota para o painel web/mobile ler a telemetria mais recente de forma assíncrona.

### 2. Modificações em `backend/cardioia_agents.py`
*   Refatorar para exportar as funções de forma que a API FastAPI possa chamá-las de maneira assíncrona e dinâmica, sem rodar a simulação fixa do `main()`.

### 3. Gerenciamento de Dependências
*   Garantir a instalação das bibliotecas: `fastapi`, `uvicorn`, `python-multipart`.

---

## 📋 Próximos Passos
1. **Aprovação do Plano:** Após sua revisão, inicializaremos a escrita do código.
2. **Escrita do Servidor API:** Implementação em `backend/app.py`.
3. **Refatoração dos Agentes:** Adaptação em `backend/cardioia_agents.py`.
4. **Testes Locais:** Executar a API localmente e validar o recebimento de requisições.
5. **Sincronização com o Repositório:** Realizar o commit e `git push` conforme a regra global do usuário.
