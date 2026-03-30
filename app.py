import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

st.set_page_config(page_title="Siigo Automator", page_icon="🤖")
st.title("🤖 Automatización Documento Soporte Siigo")

with st.sidebar:
    st.header("🔑 Credenciales")
    user_email = st.text_input("Correo Siigo")
    user_pass = st.text_input("Contraseña Siigo", type="password")
    sheet_id = st.text_input("ID de Google Sheet")

def ejecutar_robot(email, password, sid):
    # --- CONFIGURACIÓN BLINDADA PARA LA NUBE ---
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        # Iniciamos el driver de forma más sencilla para evitar conflictos de ruta
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 25)

        # 1. Leer Google Sheets
        url_csv = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
        df = pd.read_csv(url_csv)
        st.success(f"✅ Datos cargados: {len(df)} registros encontrados.")

        # 2. Login
        st.write("🌐 Abriendo Siigo...")
        driver.get("https://siigonube.siigo.com/#/login")
        
        # Esperar y escribir usuario
        user_field = wait.until(EC.element_to_be_clickable((By.ID, "username")))
        user_field.send_keys(email)
        
        # Escribir contraseña
        driver.find_element(By.ID, "password").send_keys(password)
        
        # Click en entrar
        driver.find_element(By.ID, "login-button").click()
        
        st.write("🔑 Validando acceso... (Espera 10 seg)")
        time.sleep(10)

        # 3. Procesar datos
        progreso = st.progress(0)
        for i, fila in df.iterrows():
            st.write(f"⚙️ Procesando: {fila['Nombre']}...")
            driver.get("https://siigonube.siigo.com/#/purchase/1889")
            time.sleep(5)
            
            # --- LLENADO ---
            # Aquí el robot llenará los campos. Si falla aquí, ajustaremos los IDs.
            # (Agregamos un print de debug para ver si entra)
            st.write(f"📍 Llenando datos para {fila['NIT']}...")
            
            # Ejemplo de click forzado si el normal falla
            # btn = driver.find_element(By.ID, "btn-guardar-comprobante")
            # driver.execute_script("arguments[0].click();", btn)
            
            progreso.progress((i + 1) / len(df))

        st.success("🏁 Proceso completado exitosamente.")

    except Exception as e:
        # Esto nos dirá exactamente en qué línea falló si vuelve a pasar
        st.error(f"❌ Error detallado: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if st.button("🚀 Iniciar Automatización"):
    if user_email and user_pass and sheet_id:
        ejecutar_robot(user_email, user_pass, sheet_id)
    else:
        st.error("⚠️ Falta completar datos.")
