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
        # 1. Leer Datos desde Google Sheets
        st.write("📊 Leyendo datos del Google Sheet...")
        url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        df = pd.read_csv(url_csv)
        df.columns = df.columns.str.strip() # Limpia espacios para evitar Error 'Nombre'
        st.success(f"✅ {len(df)} registros encontrados.")

        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 25)

        for i, fila in df.iterrows():
            # Extraer variables de la hoja (según tu imagen 5ea704)
            nit = str(fila['Nit'])
            cuenta = str(fila['Cuenta'])
            # Limpiar el valor: quitar puntos de miles y tomar la parte entera
            valor = str(fila['ValorUnitario']).replace('.', '').split(',')[0]
            nombre_proveedor = fila['Nombre']
            observacion = fila['Observacion']

            st.write(f"⚙️ Procesando a: **{nombre_proveedor}**...")
            driver.get(URL_SOPORTE)
            
            # --- LLENADO DE CAMPOS ---
            # 1. Proveedor
            campo_prov = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@placeholder, 'proveedor')]")))
            campo_prov.send_keys(nit)
            time.sleep(2)
            campo_prov.send_keys(Keys.ENTER)

            # 2. Producto / Cuenta Contable
            campo_cta = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'buscar')]")))
            campo_cta.send_keys(cuenta)
            time.sleep(2)
            campo_cta.send_keys(Keys.ENTER)

            # 3. Valor Unitario
            campo_val = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'unit_value')]")))
            campo_val.clear()
            campo_val.send_keys(valor)

            # 4. Observación (Corregido el error de sintaxis aquí)
            if pd.notna(observacion):
                try:
                    campo_obs = driver.find_element(By.XPATH, "//textarea[contains(@name, 'observation')]")
                    campo_obs.send_keys(str(observacion))
                except: 
                    pass # Si no encuentra el campo, continúa

            # --- GUARDAR AUTOMÁTICAMENTE ---
            st.write("💾 Guardando documento en Siigo...")
            # XPath para el botón "Guardar" verde (imagen 5ea6ca)
            btn_guardar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'success') and contains(., 'Guardar')]")))
            driver.execute_script("arguments[0].click();", btn_guardar)
            
            # --- CAPTURAR COMPROBANTE POR PANTALLA ---
            time.sleep(6) 
            try:
                # Busca el texto del nuevo documento generado
                elemento_nro = driver.find_element(By.XPATH, "//*[contains(text(), 'DS-')]")
                nro_comprobante = elemento_nro.text
                st.success(f"✅ **{nombre_proveedor}** guardado. Comprobante: `{nro_comprobante}`")
            except:
                st.warning(f"✔️ **{nombre_proveedor}** guardado, pero no se pudo leer el número DS.")

        st.balloons()
        st.success("🏁 ¡Proceso completado!")

    except Exception as e:
        st.error(f"❌ Error general: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if st.button("🚀 Iniciar Llenado y Guardado"):
    ejecutar_rellenado()
