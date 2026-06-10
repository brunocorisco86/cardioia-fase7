# 🔌 CardioIA - Subsistema IoT (MicroPython + Wokwi)

Este diretório contém a lógica de hardware e o circuito esquemático para a simulação da telemetria de sensores médicos em tempo real para a plataforma CardioIA.

---

## 🛠️ Esquema de Hardware e Conexões

O circuito é baseado no microcontrolador **ESP32** simulado no **Wokwi** e utiliza os seguintes componentes:

| Componente | Função | Pinos no ESP32 |
| :--- | :--- | :--- |
| **Potenciômetro Analógico** | Simula a leitura de Frequência Cardíaca (BPM) | **GPIO 34** (Entrada ADC1_CH6) |
| **Display OLED SSD1306 (I2C)** | Interface local que exibe batimentos, temperatura e status de rede | **GPIO 22** (SCL), **GPIO 21** (SDA) |
| **LED Verde** | Sinaliza estado clínico de normalidade | **GPIO 12** (Saída Digital) |
| **LED Vermelho** | Sinaliza estado clínico de risco/alerta ativo | **GPIO 13** (Saída Digital) |
| **Buzzer Piezoelétrico** | Emite sinal sonoro intermitente em caso de risco clínico | **GPIO 14** (Saída Digital/PWM) |
| **Resistores (2x 220Ω)** | Limitação de corrente para os LEDs de sinalização | Conectados em série aos catodos dos LEDs |

---

## 🚀 Como Executar a Simulação no Wokwi

1. Acesse o site do [Wokwi](https://wokwi.com/).
2. Crie um novo projeto escolhendo a placa **ESP32** rodando **MicroPython**.
3. Na aba do código (`main.py`), copie e cole o conteúdo do arquivo [`iot/main.py`](main.py).
4. Na aba de estrutura do circuito (`diagram.json`), cole o conteúdo do arquivo [`iot/diagram.json`](diagram.json) para que o circuito, fiação e componentes sejam montados automaticamente na tela.
5. Inicie a simulação clicando no botão **Play** (Iniciar).
6. Gire o potenciômetro para alterar os batimentos cardíacos:
   - **Girar para a esquerda (valores baixos < 50 bpm):** Ativa o alerta clínico de bradicardia (LED Vermelho acende, Buzzer bipa e a tela OLED exibe `! RISCO ELEVADO !`).
   - **Girar para a direita (valores altos > 100 bpm):** Ativa o alerta de taquicardia com simulação de febre (LED Vermelho acende, Buzzer bipa e a tela OLED exibe `! RISCO ELEVADO !`).
   - **Posição central (50 a 100 bpm):** Estado clínico normal (LED Verde acende, tela OLED exibe `Sinais Normais`).

---

## 📡 Integração de Rede (HTTP Telemetry)

O firmware tenta conectar ao Wi-Fi padrão de simulação do Wokwi (`Wokwi-GUEST`) e envia os dados coletados a cada **3 segundos** para a API do backend local através da rota:
`POST http://10.0.2.2:8000/api/telemetry`

> 💡 **Nota de Rede:** No simulador Wokwi, o endereço IP `10.0.2.2` é uma rota de gateway especial usada para alcançar o `localhost` da máquina hospedeira que está executando o backend FastAPI.
