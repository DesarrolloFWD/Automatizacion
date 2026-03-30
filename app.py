import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURACIÓN FIJA ---
SHEET_ID = "1xam93zbK1A8Ujt1Sv7wdrUfoFcaMeeCNRTcENqwELKM"
URL_SOPORTE = "https://siigonube.siigo.com/#/purchase/1889"

st.set_page_config(page_title="Siigo Rellenado Automático", page_icon="📝")
st.title("📝 Rellenado de Documento Soporte")
st.markdown(f"""
**Instrucciones:**
1. Abre Siigo en otra pestaña de este navegador e inicia sesión.
2. Una vez logueado, regresa aquí y presiona el botón.
""")

def ejecutar_rellenado():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.binary_location = "/usr/bin/chromium" 
    service = Service("/usr/bin/chromedriver")

    try:
        # 1. Leer Datos
        st.write("📊 Leyendo datos del Google Sheet...")
        url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        df = pd.read_csv(url_csv)
        st.success(f"✅ {len(df)} registros encontrados.")

        # 2. Iniciar Navegador
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 20)

        # 3. Ir directo a la creación
        st.write(f"🌐 Abriendo ruta de creación...")
        driver.get(URL_SOPORTE)
        
        # PROCESO DE LLENADO POR CADA FILA
        progreso = st.progress(0)
        for i, fila in df.iterrows():
            st.write(f"⚙️ Rellenando datos de: **{fila['Nombre']}**...")
            
            # Esperar a que el campo de NIT esté listo
            # Usamos un selector genérico que busque por placeholder
            try:
                campo_nit = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[contains(@placeholder, 'proveedor')]")))
                campo_nit.clear()
                campo_nit.send_keys(str(fila['NIT']))
                time.sleep(3) # Espera para que Siigo cargue el tercero

                # Rellenar Producto/Servicio
                campo_prod = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'ítem')]")
                campo_prod.send_keys(fila['Producto'])

                # Rellenar Valor
                campo_valor = driver.find_element(By.XPATH, "//input[@name='valor_unitario' or contains(@id, 'unit_value')]")
                campo_valor.send_keys(str(fila['Valor']))

                st.info(f"📍 Datos de {fila['Nombre']} posicionados. Revisa y guarda manualmente.")
                
                # Nota: No hacemos clic en GUARDAR automáticamente para que el usuario
                # valide que la sesión sigue activa y los datos son correctos.
                
            except Exception as e_fila:
                st.error(f"❌ Error en la fila {i+1}: Verifica si la sesión de Siigo expiró.")
            
            progreso.progress((i + 1) / len(df))
            break # Hacemos solo el primero para probar estabilidad

        st.success("🏁 Proceso de carga inicial finalizado.")

    except Exception as e:
        st.error(f"❌ Error general: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if st.button("🚀 Iniciar Rellenado Automático"):
    ejecutar_rellenado()
