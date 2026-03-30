import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# --- CONFIGURACIÓN ---
SHEET_ID = "1xam93zbK1A8Ujt1Sv7wdrUfoFcaMeeCNRTcENqwELKM"
URL_SOPORTE = "https://siigonube.siigo.com/#/purchase/1889"

st.set_page_config(page_title="Siigo Auto-Fill", page_icon="📝")
st.title("📝 Rellenado y Guardado de Documento Soporte")

def ejecutar_rellenado():
    options = Options()
    options.add_argument('--headless=new') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = "/usr/bin/chromium" 
    service = Service("/usr/bin/chromedriver")

    try:
        # 1. Leer Datos
        st.write("📊 Leyendo datos del Google Sheet...")
        url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        df = pd.read_csv(url_csv)
        
        # --- LIMPIEZA DE COLUMNAS (Para arreglar el error 'Nit') ---
        df.columns = df.columns.astype(str).str.strip() # Quita espacios
        
        # Mostrar las columnas detectadas para depuración
        st.write(f"Columnas detectadas en tu Excel: `{list(df.columns)}`")
        
        if 'Nit' not in df.columns:
            st.error("❌ No encontré la columna 'Nit'. Revisa que en el Excel diga exactamente 'Nit'.")
            return

        st.success(f"✅ {len(df)} registros encontrados.")

        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 25)

        for i, fila in df.iterrows():
            # Extraer variables con manejo de errores por si faltan columnas
            try:
                nit = str(fila['Nit']).strip()
                cuenta = str(fila['Cuenta']).strip()
                valor = str(fila['ValorUnitario']).replace('.', '').split(',')[0].strip()
                nombre_prov = fila['Nombre']
                obs = fila['Observacion'] if 'Observacion' in df.columns else ""
            except KeyError as e:
                st.error(f"❌ Falta la columna: {e}")
                break

            st.write(f"⚙️ Procesando a: **{nombre_prov}**...")
            driver.get(URL_SOPORTE)
            
            # --- LLENADO DE CAMPOS ---
            # Proveedor
            campo_prov = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@placeholder, 'proveedor')]")))
            campo_prov.send_keys(nit)
            time.sleep(2)
            campo_prov.send_keys(Keys.ENTER)

            # Producto / Cuenta
            campo_cta = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'buscar')]")))
            campo_cta.send_keys(cuenta)
            time.sleep(2)
            campo_cta.send_keys(Keys.ENTER)

            # Valor
            campo_val = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'unit_value')]")))
            campo_val.clear()
            campo_val.send_keys(valor)

            # --- GUARDAR ---
            st.write("💾 Guardando...")
            btn_guardar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'success') and contains(., 'Guardar')]")))
            driver.execute_script("arguments[0].click();", btn_guardar)
            
            time.sleep(6)
            st.success(f"✅ **{nombre_prov}** procesado correctamente.")

        st.balloons()

    except Exception as e:
        st.error(f"❌ Error general: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if st.button("🚀 Iniciar Llenado y Guardado"):
    ejecutar_rellenado()
