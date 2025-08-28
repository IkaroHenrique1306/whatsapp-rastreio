# ============================================================
# Sistema de Rastreamento de Encomendas via WhatsApp
# Desenvolvido por:
#   Íkaro Henrique Marçal Alexandre
#   Matheus Kioshi Fernandes Numata
#
# © 2025 - Todos os direitos reservados.
# Este software é propriedade intelectual dos autores.
# A reprodução, modificação ou distribuição não autorizada
# é estritamente proibida.
# ============================================================

import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from datetime import datetime
import os

# ======================== CONFIG ========================
API_KEY = "1ArXSVVpYg3PUpG-5W8llyEeq0ySyhGVZYO1Nhbc4tA"
INTERVALO = 60  # segundos entre verificações
VPS_URL = "http://68.168.216.136:5000/dados"
USER_DATA_DIR = os.path.join(os.getcwd(), "whatsapp_profile")
# ========================================================

# ===== Pede nome da vendedora =====
VENDEDORA = input("Digite o nome da vendedora: ").strip()

# ===== Função para consultar o Wonca Labs =====
def obter_status(codigo):
    headers = {"Content-Type": "application/json", "Authorization": f"Apikey {API_KEY}"}
    payload = {"code": codigo}
    try:
        response = requests.post(
            "https://api-labs.wonca.com.br/wonca.labs.v1.LabsService/Track",
            headers=headers,
            json=payload,
            timeout=10
        )
        dados = json.loads(response.json().get("json", "{}"))
        eventos = dados.get("eventos", [])
        if eventos:
            ultimo = eventos[0]
            descricao = ultimo.get("descricaoFrontEnd", "Sem descrição")
            cidade = ultimo.get("unidade", {}).get("endereco", {}).get("cidade", "")
            uf = ultimo.get("unidade", {}).get("endereco", {}).get("uf", "")
            return f"{descricao} ({cidade}/{uf})"
        return "Não Encontrado"
    except Exception as e:
        print(f"❌ Erro ao consultar status de {codigo}: {e}")
        return "Erro"

# ===== Função para enviar mensagem no WhatsApp =====
def enviar_mensagens(mensagens):
    if not mensagens:
        return

    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)

    options = EdgeOptions()
    options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    options.add_argument("--profile-directory=Default")

    driver = webdriver.Edge(service=EdgeService(), options=options)
    wait = WebDriverWait(driver, 30)

    try:
        for numero, mensagem in mensagens.items():
            print(f"📩 Abrindo chat com {numero}...")
            driver.get(f"https://web.whatsapp.com/send?phone={numero}")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']")))
            time.sleep(2)

            textbox = driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']")
            for line in mensagem.split("\n"):
                textbox.send_keys(line)
                textbox.send_keys(Keys.SHIFT, Keys.ENTER)
                time.sleep(0.1)
            textbox.send_keys(Keys.ENTER)
            time.sleep(2)
            print(f"✅ Mensagem enviada para {numero}!")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagens: {e}")
        driver.save_screenshot("erro.png")
    finally:
        driver.quit()
        print("📴 WhatsApp Web fechado.")

# ===== Loop principal =====
ultimo_status_enviado = {}

while True:
    try:
        resp = requests.get(VPS_URL, timeout=10)
        todos_dados = resp.json()

        contatos = todos_dados.get(VENDEDORA, {})
        mensagens_para_enviar = {}

        for numero, codigo in contatos.items():
            status_atual = obter_status(codigo)
            if ultimo_status_enviado.get(numero) != status_atual:
                mensagens_para_enviar[numero] = f"""ENCOMENDA - Status do Rastreamento

- Código: {codigo}
- Status: {status_atual}
- Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Enviado automaticamente."""
                ultimo_status_enviado[numero] = status_atual

        if mensagens_para_enviar:
            print("📱 Novas atualizações! Abrindo WhatsApp Web...")
            enviar_mensagens(mensagens_para_enviar)
        else:
            print("⏳ Nenhuma mudança de status. Aguardando...")

        time.sleep(INTERVALO)

    except Exception as e:
        print(f"❌ Erro no loop principal: {e}")
        time.sleep(60)
