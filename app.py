import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

st.set_page_config(page_title="Siigo Automator", page_icon="🤖")
st.title("🤖 Automatización Documento Soporte Siigo")

# --- INTERFAZ LATERAL ---
with st.sidebar:
    st.header("🔑 Credenciales")
    user_email = st.text_input("Correo Siigo")
    user_pass = st.text_input("Contraseña Siigo", type="password")
    sheet_id = st.text_input("ID de Google Sheet")

def ejecutar_robot(email, password, sid):
    # Configuración de Chrome para Streamlit Cloud
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080') # Para que los botones no se escondan
    
    try:
        # Intentar iniciar el driver
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 30) # Espera de hasta 30 segundos

        # 1. Leer Google Sheets
        url_csv = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
        df = pd.read_csv(url_csv)
        st.success(f"✅ Datos cargados: {len(df)} registros encontrados.")

        # 2. Login
        st.write("🌐 Abriendo Siigo...")
        driver.get("https://siigonube.siigo.com/#/login")
        
        user_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        user_field.send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "login-button").click()
        
        st.write("🔑 Iniciando sesión... (esperando 10s)")
        time.sleep(10) # Tiempo extra para pasar pantallas de carga inicial

        # 3. Ciclo de Carga
        bar = st.progress(0)
        for i, fila in df.iterrows():
            st.write(f"⚙️ Procesando: {fila['Nombre']}...")
            driver.get("https://siigonube.siigo.com/#/purchase/1889")
            
            # Esperar a que el campo de NIT sea visible
            input_nit = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[contains(@placeholder, 'proveedor')]")))
            input_nit.send_keys(str(fila['NIT']))
            time.sleep(3) # Pausa para que el sistema busque el nombre

            # Llenado de Ítem y Valor
            driver.find_element(By.XPATH, "//input[contains(@placeholder, 'ítem')]").send_keys(fila['Producto'])
            driver.find_element(By.XPATH, "//input[@name='valor_unitario']").send_keys(str(fila['Valor']))

            # Click en Guardar
            btn_guardar = driver.find_element(By.ID, "btn-guardar-comprobante")
            driver.execute_script("arguments[0].click();", btn_save) # Click forzado por JS para evitar errores
            
            bar.progress((i + 1) / len(df))
            st.write(f"✔️ {fila['Nombre']} Guardado.")
            time.sleep(2)

        st.balloons()
        st.success("🏁 Proceso completado.")

    except Exception as e:
        st.error(f"❌ Error durante la ejecución: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if st.button("🚀 Iniciar Automatización"):
    if user_email and user_pass and sheet_id:
        ejecutar_robot(user_email, user_pass, sheet_id)
    else:
        st.error("⚠️ Falta completar datos.")
