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

with st.sidebar:
    st.header("🔑 Credenciales")
    user_email = st.text_input("Correo Siigo")
    user_pass = st.text_input("Contraseña Siigo", type="password")
    sheet_id = st.text_input("ID de Google Sheet")

def ejecutar_robot(email, password, sid):
    try:
        # PASO 1: LEER DATOS (Sin encender navegador aún)
        st.write("📊 **Paso 1:** Leyendo datos de Google Sheets...")
        url_csv = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
        df = pd.read_csv(url_csv)
        st.success(f"✅ ¡Éxito! {len(df)} registros listos para procesar.")

        # PASO 2: CONFIGURACIÓN LIGERA DEL NAVEGADOR
        st.write("⚙️ **Paso 2:** Encendiendo el robot (modo bajo consumo)...")
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage') # Clave para evitar error de memoria
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920x1080')
        # ¡EL SECRETO!: No cargar imágenes ni CSS pesado para ahorrar RAM
        options.add_argument('--blink-settings=imagesEnabled=false') 
        
        options.binary_location = "/usr/bin/chromium" 
        service = Service("/usr/bin/chromedriver")
        
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 20)
        st.success("✅ ¡Robot encendido sin problemas!")

        # PASO 3: ENTRAR A SIIGO
        st.write("🌐 **Paso 3:** Cargando la página de Siigo...")
        driver.get("https://siigonube.siigo.com/#/login")
        st.success("✅ ¡Página cargada sin explotar!")
        
        # PASO 4: LOGIN
        st.write("🔑 **Paso 4:** Ingresando usuario y contraseña...")
        user_input = wait.until(EC.element_to_be_clickable((By.ID, "username")))
        user_input.send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "login-button").click()
        
        st.write("⏳ Esperando a que cargue el menú principal (10 seg)...")
        time.sleep(10)

        # PASO 5: NAVEGACIÓN
        st.write("📍 **Paso 5:** Buscando la ruta de Documentos Soporte...")
        driver.get("https://siigonube.siigo.com/#/purchase/1889")
        time.sleep(5)
        
        st.success("🏁 ¡LLEGAMOS A LA META DE PRUEBA! La conexión es 100% estable.")

    except Exception as e:
        st.error(f"❌ El proceso falló en el último paso mostrado. Error técnico: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if st.button("🚀 Iniciar Automatización"):
    if user_email and user_pass and sheet_id:
        ejecutar_robot(user_email, user_pass, sheet_id)
    else:
        st.error("⚠️ Falta completar datos.")
