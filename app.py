import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- INTERFAZ DE USUARIO ---
st.set_page_config(page_title="Siigo Automator", page_icon="🤖")
st.title("🤖 Automatización Documento Soporte Siigo")

with st.sidebar:
    st.header("🔑 Credenciales")
    user_email = st.text_input("Correo Siigo")
    user_pass = st.text_input("Contraseña Siigo", type="password")
    sheet_id = st.text_input("ID de Google Sheet")

# --- FUNCIÓN DEL ROBOT ---
def ejecutar_robot(email, password, sid):
    # Configuración para servidores (Headless)
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # En Streamlit Cloud, el driver se instala automáticamente en esta ruta
    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)

    try:
        # 1. Leer Google Sheets
        url_csv = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
        df = pd.read_csv(url_csv)
        st.success(f"✅ Datos cargados: {len(df)} registros encontrados.")

        # 2. Login en Siigo
        driver.get("https://siigonube.siigo.com/#/login")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "login-button").click()
        time.sleep(7) # Espera carga inicial

        # 3. Proceso de llenado
        bar = st.progress(0)
        for i, fila in df.iterrows():
            st.write(f"⚙️ Procesando NIT: {fila['NIT']}...")
            
            # Ir directo a la creación de DS
            driver.get("https://siigonube.siigo.com/#/purchase/1889")
            
            # Llenar NIT
            input_nit = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'proveedor')]")))
            input_nit.send_keys(str(fila['NIT']))
            time.sleep(3) # Esperar a que Siigo reconozca al proveedor

            # Llenar Producto y Valor (Ajustar selectores según la web de Siigo)
            driver.find_element(By.XPATH, "//input[contains(@placeholder, 'ítem')]").send_keys(fila['Producto'])
            driver.find_element(By.XPATH, "//input[@name='valor_unitario']").send_keys(str(fila['Valor']))

            # Acción de GUARDAR (Solo guarda, no envía a la DIAN)
            btn_guardar = driver.find_element(By.ID, "btn-guardar-comprobante")
            btn_guardar.click()
            
            bar.progress((i + 1) / len(df))
            st.write(f"✔️ {fila['Nombre']} Guardado.")
            time.sleep(2)

        st.balloons()
        st.success("🏁 Proceso completado. Revisa tus borradores en Siigo.")

    except Exception as e:
        st.error(f"❌ Error durante la ejecución: {e}")
    finally:
        driver.quit()

# Botón de inicio
if st.button("🚀 Iniciar Automatización"):
    if user_email and user_pass and sheet_id:
        ejecutar_robot(user_email, user_pass, sheet_id)
    else:
        st.error("⚠️ Falta completar datos en la barra lateral.")