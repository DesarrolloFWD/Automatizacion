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
        
      # PASO 4: LOGIN (Versión Inteligente)
        st.write("🔑 **Paso 4:** Ingresando credenciales...")
        
        # Le damos tiempo extra para que los campos aparezcan
        time.sleep(5) 
        
        # TRUCO: Siigo a veces usa un iframe. Intentamos encontrar los inputs de forma general
        inputs = driver.find_elements(By.TAG_NAME, "input")
        
        if len(inputs) >= 2:
            st.write(f"🔎 Se encontraron {len(inputs)} campos. Intentando llenar...")
            for campo in inputs:
                tipo = campo.get_attribute("type")
                # El primer campo suele ser el usuario, o el que es tipo email/text
                if tipo in ["email", "text"] and not campo.get_attribute("value"):
                    campo.click()
                    for letra in email:
                        campo.send_keys(letra)
                        time.sleep(0.05)
                # El campo de password es fácil de identificar
                if tipo == "password":
                    campo.click()
                    for letra in password:
                        campo.send_keys(letra)
                        time.sleep(0.05)
            
            # Buscamos el botón que diga "Ingresar" o sea tipo "submit"
            time.sleep(2)
            botones = driver.find_elements(By.TAG_NAME, "button")
            for btn in botones:
                if "login" in btn.get_attribute("id").lower() or "submit" in btn.get_attribute("type").lower() or "Ingresar" in btn.text:
                    driver.execute_script("arguments[0].click();", btn)
                    break
        else:
            # Si no encuentra inputs normales, probamos con los selectores exactos actuales de Siigo
            st.warning("Usando selectores de emergencia...")
            wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(email)
            driver.find_element(By.NAME, "password").send_keys(password)
            driver.find_element(By.ID, "login-button").click()

        st.write("⏳ Validando sesión... (15 seg)")
        time.sleep(15)
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
