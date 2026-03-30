import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        # Iniciamos el driver de la forma más simple posible
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 20)

        # 1. Leer Datos
        url_csv = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
        df = pd.read_csv(url_csv)
        st.success(f"✅ {len(df)} registros cargados.")

        # 2. Login
        st.write("🌐 Conectando a Siigo...")
        driver.get("https://siigonube.siigo.com/#/login")
        
        # Esperar al campo de usuario
        user_input = wait.until(EC.element_to_be_clickable((By.ID, "username")))
        user_input.send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "login-button").click()
        
        st.write("🔑 Iniciando sesión... (espera 10s)")
        time.sleep(10)

        # 3. Proceso
        for i, fila in df.iterrows():
            st.write(f"⚙️ Preparando DS para: {fila['Nombre']}")
            driver.get("https://siigonube.siigo.com/#/purchase/1889")
            time.sleep(5)
            # Aquí irían los comandos de llenado una vez logremos entrar
            
        st.success("🏁 Proceso terminado.")

    except Exception as e:
        st.error(f"❌ Error de conexión: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if st.button("🚀 Iniciar Automatización"):
    if user_email and user_pass and sheet_id:
        ejecutar_robot(user_email, user_pass, sheet_id)
    else:
        st.error("⚠️ Falta completar datos.")
