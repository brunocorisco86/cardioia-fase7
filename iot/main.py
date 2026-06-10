import time
import network
import urequests
import random
import machine

# Configurações do Wi-Fi (Substituir com os dados da rede local)
WIFI_SSID = "Wokwi-GUEST"  # SSID padrão usado no simulador Wokwi
WIFI_PASSWORD = ""         # Senha do Wokwi-GUEST é vazia

# Configurações do Backend (Substituir pelo IP/Porta onde a API está rodando)
# No simulador Wokwi, para conectar ao localhost da máquina hospedeira, usa-se o IP "10.0.2.2"
BACKEND_URL = "http://10.0.2.2:8000/api/telemetry"

# Configuração de Pinos para Simulação no Hardware (ESP32)
# Potenciômetro no pino ADC 34 (simulando sensor de batimentos cardíacos)
adc_pin = machine.ADC(machine.Pin(34))
try:
    # Ajusta a atenuação no ESP32 para permitir leitura de até 3.3V (faixa completa de 0 a 4095)
    adc_pin.atten(machine.ADC.ATTN_11DB)
except AttributeError:
    # Para outros microcontroladores como Raspberry Pi Pico que não utilizam esta chamada
    pass

def conectar_wifi():
    """Realiza a conexão do dispositivo com o Wi-Fi local."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando ao Wi-Fi %s..." % WIFI_SSID)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Aguarda a conexão por até 10 segundos
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
    # Lê valor bruto do potenciômetro (0 a 4095)
    valor_adc = adc_pin.read()
    
    # Mapeia a leitura analógica de 12 bits para bpm (40 a 140 bpm)
    frequencia_cardiaca = int(40 + (valor_adc / 4095.0) * 100)
    
    # Simulação de temperatura corporal realista (36.0°C a 39.5°C)
    if frequencia_cardiaca > 100:
        # Se os batimentos estiverem muito altos, simula um quadro febril correspondente
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
        print("[IoT] Dados retornados pelo servidor:", response.text)
        response.close()
    except Exception as e:
        print("[IoT] Erro ao enviar telemetria para a API:", e)

def main():
    print("=========================================================")
    print("   CARDIOIA - Firmware IoT (MicroPython Simulador Wokwi) ")
    print("=========================================================")
    
    # Conecta no Wi-Fi no início
    conectar_wifi()
    
    while True:
        wlan = network.WLAN(network.STA_IF)
        
        # Se o sinal do Wi-Fi cair, reconecta
        if not wlan.isconnected():
            print("\n[Wi-Fi] Conexão inativa. Reconectando...")
            conectar_wifi()
            
        # Lê sinais vitais
        temp, fc = ler_sensores()
        
        # Envia dados apenas se a rede estiver operacional
        if wlan.isconnected():
            enviar_telemetria(temp, fc)
        else:
            print("\n[IoT] Telemetria não enviada (Wi-Fi desconectado).")
            
        # Intervalo de leitura de 5 segundos
        time.sleep(5)

if __name__ == "__main__":
    main()
