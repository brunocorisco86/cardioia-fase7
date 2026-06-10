import time
import network
import urequests
import random
import machine
import ssd1306

# Configurações do Wi-Fi (Substituir com os dados da rede local)
WIFI_SSID = "Wokwi-GUEST"  # SSID padrão usado no simulador Wokwi
WIFI_PASSWORD = ""         # Senha do Wokwi-GUEST é vazia

# Configurações do Backend (Substituir pelo IP/Porta onde a API está rodando)
# No simulador Wokwi, para conectar ao localhost da máquina hospedeira, usa-se o IP "10.0.2.2"
BACKEND_URL = "http://10.0.2.2:8000/api/telemetry"

# Configuração de Pinos para Hardware (ESP32)
# Potenciômetro no pino ADC 34 (simulando sensor de batimentos cardíacos)
adc_pin = machine.ADC(machine.Pin(34))
try:
    adc_pin.atten(machine.ADC.ATTN_11DB)
except AttributeError:
    pass

# Leds de Alerta Clínico
led_vermelho = machine.Pin(13, machine.Pin.OUT)
led_verde = machine.Pin(12, machine.Pin.OUT)

# Buzzer para Alerta Sonoro
buzzer = machine.Pin(14, machine.Pin.OUT)

# Display OLED SSD1306 (I2C)
# Conexão I2C0 no ESP32: SCL (GPIO 22), SDA (GPIO 21)
try:
    i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)
    oled_ativo = True
    print("[OLED] Display inicializado com sucesso!")
except Exception as e:
    oled_ativo = False
    print("[OLED] Erro ao inicializar display OLED:", e)

def atualizar_display(status_wifi, fc, temp, alerta_ativo):
    """Atualiza as informações médicas e de rede na tela OLED local."""
    if not oled_ativo:
        return
        
    try:
        oled.fill(0)
        
        # Cabeçalho
        oled.text("=== CardioIA ===", 4, 0)
        
        # Status de Rede
        oled.text("Rede: %s" % status_wifi, 0, 16)
        
        # Leituras Clínicas
        oled.text("FC: %d BPM" % fc, 0, 32)
        oled.text("Temp: %.1f C" % temp, 0, 44)
        
        # Alerta Clínico
        if alerta_ativo:
            oled.text("! RISCO ELEVADO !", 0, 56)
        else:
            oled.text("Sinais Normais", 0, 56)
            
        oled.show()
    except Exception as e:
        print("[OLED] Erro ao atualizar tela:", e)

def conectar_wifi():
    """Realiza a conexão do dispositivo com o Wi-Fi local."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando ao Wi-Fi %s..." % WIFI_SSID)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        tentativas = 0
        while not wlan.isconnected() and tentativas < 10:
            time.sleep(1)
            tentativas += 1
            print(".", end="")
            
    if wlan.isconnected():
        print("\n[Wi-Fi] Conectado com Sucesso!")
        print("[Wi-Fi] Configurações de rede:", wlan.ifconfig())
        return True
    else:
        print("\n[Wi-Fi] Falha ao conectar ao Wi-Fi.")
        return False

def ler_sensores():
    """
    Lê os dados simulados dos sensores de saúde.
    - Frequência cardíaca: Mapeia a leitura analógica do potenciômetro (0-4095) para (40-140 bpm)
    - Temperatura: Gera flutuação realista simulando febre em casos de batimentos altos.
    """
    valor_adc = adc_pin.read()
    
    # Mapeia a leitura analógica de 12 bits para bpm (40 a 140 bpm)
    frequencia_cardiaca = int(40 + (valor_adc / 4095.0) * 100)
    
    # Simulação de temperatura corporal realista (36.0°C a 39.5°C)
    if frequencia_cardiaca > 100:
        temperatura = round(random.uniform(37.6, 39.4), 1)
    else:
        temperatura = round(random.uniform(36.1, 37.2), 1)
        
    return temperatura, frequencia_cardiaca

def enviar_telemetria(temperatura, frequencia_cardiaca):
    """Envia as leituras dos sensores via HTTP POST em formato JSON para o backend."""
    payload = {
        "temperatura": temperatura,
        "frequencia_cardiaca": frequencia_cardiaca
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("\n[IoT] Enviando telemetria: Temp=%s°C, FC=%s bpm..." % (temperatura, frequencia_cardiaca))
    
    try:
        response = urequests.post(BACKEND_URL, json=payload, headers=headers)
        print("[IoT] Resposta do backend - Status HTTP:", response.status_code)
        response.close()
        return True
    except Exception as e:
        print("[IoT] Erro ao enviar telemetria para a API:", e)
        return False

def gerenciar_alertas_hardware(temp, fc):
    """Aciona LEDs e Buzzer locais de acordo com limites clínicos de risco."""
    alerta_ativo = False
    
    # Condições de alerta: taquicardia (>100), bradicardia (<50) ou febre (>38°C)
    if fc > 100 or fc < 50 or temp > 38.0:
        alerta_ativo = True
        
    if alerta_ativo:
        # Liga LED vermelho e desliga verde
        led_vermelho.value(1)
        led_verde.value(0)
        
        # Emite bip de alerta intermitente no Buzzer
        buzzer.value(1)
        time.sleep(0.1)
        buzzer.value(0)
    else:
        # Liga LED verde e desliga vermelho/buzzer
        led_vermelho.value(0)
        led_verde.value(1)
        buzzer.value(0)
        
    return alerta_ativo

def main():
    print("=========================================================")
    print("   CARDIOIA - Firmware IoT (MicroPython Simulador Wokwi) ")
    print("=========================================================")
    
    # Conecta no Wi-Fi no início
    conectado = conectar_wifi()
    status_inicial_rede = "Conectado" if conectado else "Desconectado"
    
    # Atualização inicial da tela
    atualizar_display(status_inicial_rede, 0, 0.0, False)
    
    while True:
        wlan = network.WLAN(network.STA_IF)
        rede_ativa = wlan.isconnected()
        status_rede = "Conectado" if rede_ativa else "Desconectado"
        
        # Se o sinal do Wi-Fi cair, reconecta
        if not rede_ativa:
            print("\n[Wi-Fi] Conexão inativa. Reconectando...")
            conectar_wifi()
            
        # Lê sinais vitais do paciente
        temp, fc = ler_sensores()
        
        # Gerencia atuadores físicos baseando-se nas leituras de risco
        alerta_ativo = gerenciar_alertas_hardware(temp, fc)
        
        # Atualiza feedbacks no display OLED
        atualizar_display(status_rede, fc, temp, alerta_ativo)
        
        # Envia dados ao backend apenas se a rede estiver operacional
        if rede_ativa:
            enviar_telemetria(temp, fc)
        else:
            print("\n[IoT] Telemetria não enviada (Wi-Fi desconectado).")
            
        # Intervalo de leitura de 3 segundos (sincronizado com o pooling do dashboard)
        time.sleep(3)

if __name__ == "__main__":
    main()
