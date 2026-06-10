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
    adc_pin.width(machine.ADC.WIDTH_12BIT) # Definir resolução para 12 bits (0-4095)
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
        # Tenta conectar por um tempo limitado, mas não bloqueia indefinidamente
        timeout_count = 0
        while not wlan.isconnected() and timeout_count < 20: # Tenta por 20 segundos
            time.sleep(1)
            timeout_count += 1
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
    print("[Sensor] Leitura ADC bruta: %d" % valor_adc)
    
    # Mapeia a leitura analógica de 12 bits para bpm (40 a 140 bpm)
    frequencia_cardiaca = int(40 + (valor_adc / 4095.0) * 100)
    print("[Sensor] Frequência Cardíaca calculada: %d BPM" % frequencia_cardiaca)
    
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
        print("[IoT] Telemetria enviada. Status: %d" % response.status_code)
        response.close()
    except Exception as e:
        print("[IoT] Erro ao enviar telemetria:", e)

# Loop Principal (faltava no código original)
def main():
    print("Iniciando CardioIA...")
    wifi_conectado = False # Inicializa como falso
    status_wifi = "OFF"
    
    # Tenta conectar Wi-Fi, mas não bloqueia o início do programa
    print("Tentando conectar ao Wi-Fi...")
    wifi_conectado = conectar_wifi()
    if wifi_conectado:
        status_wifi = "OK"
    else:
        print("\n[Wi-Fi] Não foi possível conectar. Continuará operando offline.")
        
    # Inicializa o display com o status atual
    atualizar_display(status_wifi, 0, 0, False) # Valores iniciais para FC e Temp
    
    last_telemetry_send_time = time.ticks_ms() # Inicializa o contador de tempo para telemetria
    
    while True:
        try:
            temp, fc = ler_sensores()
            alerta = fc > 100 or temp > 37.5
            
            # Controle dos LEDs e Buzzer
            if alerta:
                led_vermelho.value(1)
                led_verde.value(0)
                buzzer.value(1)
            else:
                led_vermelho.value(0)
                led_verde.value(1)
                buzzer.value(0)
                
            atualizar_display(status_wifi, fc, temp, alerta)
            
            # Envia telemetria apenas a cada 10 ciclos (2 segundos, se o sleep for 0.2)
            # Isso evita sobrecarregar o backend e mantém o display responsivo
            if wifi_conectado and (time.ticks_ms() - last_telemetry_send_time) >= 2000:
                enviar_telemetria(temp, fc)
                last_telemetry_send_time = time.ticks_ms()
                
            time.sleep(0.2) # Pequeno delay para leitura de sensores e atualização do display
            
        except Exception as e:
            print("Erro no loop principal:", e)
            time.sleep(2)

if __name__ == "__main__":
    main()
