import asyncio
import websockets
from webhook import PicPayMonitor
import time

# IP do ESP32 (use o IP mostrado no Monitor Serial do Arduino IDE)
esp32_ip = 'ws://192.168.2.110:81'  # Atualize com o IP correto do seu ESP32 e porta WebSocket (normalmente 81)

# Configuração do monitor
edge_driver_path = 'C:/Users/Gustavo Henrique/Desktop/edgedriver_win64/msedgedriver.exe'
url = 'https://monitor-negocios.picpay.com/transactions'

monitor = PicPayMonitor(driver_path=edge_driver_path, url=url)

# Função para enviar o valor para o ESP32
async def enviar_valor_esp32(valor):
    try:
        async with websockets.connect(esp32_ip) as websocket:
            print(f"Enviando valor: {valor}")
            await websocket.send(f"VALOR:{valor}")
            response = await websocket.recv()
            print(f"Resposta do ESP32 para valor: {response}")
    except Exception as e:
        print(f"Erro ao enviar valor para o ESP32: {e}")

# Função para enviar o ID para o ESP32
async def enviar_id_esp32(id_transacao):
    try:
        async with websockets.connect(esp32_ip) as websocket:
            print(f"Enviando ID: {id_transacao}")
            await websocket.send(f"ID:{id_transacao}")
            response = await websocket.recv()
            print(f"Resposta do ESP32 para ID: {response}")
    except Exception as e:
        print(f"Erro ao enviar ID para o ESP32: {e}")

# Função para monitorar transações e enviar dados ao ESP32
async def monitorar_transacoes_com_envio():
    while True:
        valor = monitor.obter_valor_ultima_transacao()
        id_transacao = monitor.obter_id_ultima_transacao()
        if valor and id_transacao:
            print(f"Valor da última transação: {valor}")
            print(f"ID: {id_transacao}")
            await enviar_valor_esp32(valor)  # Executa a função assíncrona para valor
            await enviar_id_esp32(id_transacao)  # Executa a função assíncrona para ID
        await asyncio.sleep(2.5)  # Espera de forma assíncrona
        monitor.atualizar_pagina()

if __name__ == "__main__":
    try:
        monitor.iniciar_navegador()
        monitor.acessar_painel()
        asyncio.run(monitorar_transacoes_com_envio())
    except KeyboardInterrupt:
        print("Interrupção manual. O navegador será fechado.")
    finally:
        monitor.fechar_navegador()
