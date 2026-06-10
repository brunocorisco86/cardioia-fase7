#!/bin/bash

# Configura cores para saída no console
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # Sem Cor

# Diretórios
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPORT_DIR="$SCRIPT_DIR/test_logs"
LOG_FILE="$REPORT_DIR/test_run_$(date +%Y%m%d_%H%M%S).log"

# Cria pasta de logs
mkdir -p "$REPORT_DIR"

# Inicializa arquivo de log
echo "=========================================================" > "$LOG_FILE"
echo "   CARDIOIA - RELATÓRIO DE TESTES AUTOMATIZADOS" >> "$LOG_FILE"
echo "   Executado em: $(date)" >> "$LOG_FILE"
echo "=========================================================" >> "$LOG_FILE"

echo -e "${BLUE}[CardioIA] Iniciando execução da suíte de testes unificada...${NC}"
echo -e "${BLUE}[CardioIA] Logs detalhados salvos em: $LOG_FILE${NC}"

# 1. Testes do Backend (Python pytest)
echo -e "\n${YELLOW}[1/3] Executando testes unitários do Backend (FastAPI)...${NC}"
echo -e "\n--- [1/3] Backend Tests (pytest) ---" >> "$LOG_FILE"

if [ -f "$SCRIPT_DIR/backend/venv/bin/pytest" ]; then
    "$SCRIPT_DIR/backend/venv/bin/pytest" "$SCRIPT_DIR/backend/tests/" >> "$LOG_FILE" 2>&1
    BACKEND_STATUS=$?
else
    echo "Erro: pytest não encontrado no ambiente virtual do backend." | tee -a "$LOG_FILE"
    BACKEND_STATUS=1
fi

if [ $BACKEND_STATUS -eq 0 ]; then
    echo -e "${GREEN}✔ Testes do Backend concluídos com sucesso!${NC}"
    echo "Status: SUCESSO" >> "$LOG_FILE"
else
    echo -e "${RED}✘ Falha nos testes do Backend!${NC}"
    echo "Status: FALHA" >> "$LOG_FILE"
fi

# 2. Testes do Frontend Web (Node.js test)
echo -e "\n${YELLOW}[2/3] Executando testes do Frontend Web (React/Vite)...${NC}"
echo -e "\n--- [2/3] Frontend Web Tests (node --test) ---" >> "$LOG_FILE"

# Verifica se a pasta dist existe, se não, gera o build
if [ ! -d "$SCRIPT_DIR/frontend-web/dist" ]; then
    echo "Pasta dist/ não encontrada. Gerando o build de produção..." | tee -a "$LOG_FILE"
    (cd "$SCRIPT_DIR/frontend-web" && npm run build) >> "$LOG_FILE" 2>&1
fi

node --test "$SCRIPT_DIR/frontend-web/tests/frontend.test.js" >> "$LOG_FILE" 2>&1
FRONTEND_STATUS=$?

if [ $FRONTEND_STATUS -eq 0 ]; then
    echo -e "${GREEN}✔ Testes do Frontend Web concluídos com sucesso!${NC}"
    echo "Status: SUCESSO" >> "$LOG_FILE"
else
    echo -e "${RED}✘ Falha nos testes do Frontend Web!${NC}"
    echo "Status: FALHA" >> "$LOG_FILE"
fi

# 3. Testes do Aplicativo Móvel (Node.js test)
echo -e "\n${YELLOW}[3/3] Executando testes do Aplicativo Móvel (React Native)...${NC}"
echo -e "\n--- [3/3] Mobile App Tests (node --test) ---" >> "$LOG_FILE"

node --test "$SCRIPT_DIR/mobile-app/tests/mobile.test.js" >> "$LOG_FILE" 2>&1
MOBILE_STATUS=$?

if [ $MOBILE_STATUS -eq 0 ]; then
    echo -e "${GREEN}✔ Testes do Aplicativo Móvel concluídos com sucesso!${NC}"
    echo "Status: SUCESSO" >> "$LOG_FILE"
else
    echo -e "${RED}✘ Falha nos testes do Aplicativo Móvel!${NC}"
    echo "Status: FALHA" >> "$LOG_FILE"
fi

# Resumo Final no Console
echo -e "\n${BLUE}=========================================================${NC}"
echo -e "${BLUE}                   RESUMO DOS TESTES                     ${NC}"
echo -e "${BLUE}=========================================================${NC}"

if [ $BACKEND_STATUS -eq 0 ]; then
    echo -e "Backend:         ${GREEN}PASSOU${NC}"
else
    echo -e "Backend:         ${RED}FALHOU${NC}"
fi

if [ $FRONTEND_STATUS -eq 0 ]; then
    echo -e "Frontend Web:    ${GREEN}PASSOU${NC}"
else
    echo -e "Frontend Web:    ${RED}FALHOU${NC}"
fi

if [ $MOBILE_STATUS -eq 0 ]; then
    echo -e "Mobile App:      ${GREEN}PASSOU${NC}"
else
    echo -e "Mobile App:      ${RED}FALHOU${NC}"
fi

echo -e "${BLUE}=========================================================${NC}"

# Adiciona Resumo Final ao Log
echo -e "\n=========================================================" >> "$LOG_FILE"
echo "                   RESUMO DOS TESTES                     " >> "$LOG_FILE"
echo "=========================================================" >> "$LOG_FILE"
echo "Backend:         $( [ $BACKEND_STATUS -eq 0 ] && echo 'PASSOU' || echo 'FALHOU' )" >> "$LOG_FILE"
echo "Frontend Web:    $( [ $FRONTEND_STATUS -eq 0 ] && echo 'PASSOU' || echo 'FALHOU' )" >> "$LOG_FILE"
echo "Mobile App:      $( [ $MOBILE_STATUS -eq 0 ] && echo 'PASSOU' || echo 'FALHOU' )" >> "$LOG_FILE"
echo "=========================================================" >> "$LOG_FILE"

# Verifica se tudo passou
if [ $BACKEND_STATUS -eq 0 ] && [ $FRONTEND_STATUS -eq 0 ] && [ $MOBILE_STATUS -eq 0 ]; then
    echo -e "${GREEN}Todas as suítes de testes foram validadas com SUCESSO!${NC}\n"
    exit 0
else
    echo -e "${RED}Ocorreram falhas em uma ou mais suítes de testes!${NC}\n"
    exit 1
fi
