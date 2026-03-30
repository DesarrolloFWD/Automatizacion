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
st.title("📝 Documento Soporte Siigo")

def ejecutar_rellenado():
    options = Options()
    options.add_argument('--headless=new') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = "/usr/bin/chromium" 
    service = Service("/usr/bin/chromedriver")

    try:
        # 1. Leer Datos y Limpiar Columnas
        st.write("📊 Leyendo datos del Google Sheet...")
        url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        df = pd.read_csv(url_csv)
        df.columns = df.columns.astype(str).str.strip() 
        st.success(f"✅ {len(df)} registros encontrados.")

        driver = webdriver.Chrome(service=service, options=options)
        # Aumentamos el tiempo de espera a 40 segundos para entornos lentos
        wait = WebDriverWait(driver, 40)

        for i, fila in df.iterrows():
            nit = str(fila['Nit']).strip()
            cuenta = str(fila['Cuenta']).strip()
            valor = str(fila['ValorUnitario']).replace('.', '').split(',')[0].strip()
            nombre_prov = fila['Nombre']

            st.write(f"⚙️ Procesando a: **{nombre_prov}**...")
            driver.get(URL_SOPORTE)
            
            try:
                # --- LLENADO CON ESPERAS REFORZADAS ---
                # 1. Proveedor (Esperamos a que el campo sea visible y clickeable)
                campo_prov = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@placeholder, 'proveedor')]")))
                campo_prov.click()
                campo_prov.send_keys(nit)
                time.sleep(4) # Tiempo para que Siigo busque el NIT
                campo_prov.send_keys(Keys.ENTER)
                st.write("✅ Proveedor ingresado.")

                # 2. Producto / Cuenta
                campo_cta = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'buscar')]")))
                campo_cta.send_keys(cuenta)
                time.sleep(3)
                campo_cta.send_keys(Keys.ENTER)
                st.write("✅ Cuenta contable ingresada.")

                # 3. Valor
                campo_val = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'unit_value')]")))
                campo_val.clear()
                campo_val.send_keys(valor)
                st.write("✅ Valor ingresado.")

                # --- GUARDAR ---
                st.write("💾 Guardando documento...")
                btn_guardar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'success') and contains(., 'Guardar')]")))
                driver.execute_script("arguments[0].click();", btn_guardar)
                
                # Esperar a que aparezca el mensaje de éxito o el número de DS
                time.sleep(8)
                st.success(f"✔️ **{nombre_prov}** guardado correctamente.")

            except Exception as e_fila:
                st.error(f"❌ Error procesando a {nombre_prov}. La página tardó mucho en responder.")
                # Opcional: tomar captura de pantalla para depurar
                # driver.save_screenshot(f"error_{i}.png")

        st.balloons()

    except Exception as e:
        st.error(f"❌ Error técnico: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if st.button("🚀 Iniciar Llenado y Guardado"):
    ejecutar_rellenado()
