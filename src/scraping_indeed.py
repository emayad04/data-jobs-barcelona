from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import random

# Configuración del navegador
options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

# Inicialización del driver
service = ChromeService(executable_path="./src/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

# Paso 1: Ir a Computrabajo Colombia
driver.get("https://co.computrabajo.com")

# Paso 2: Aceptar cookies si aparece
try:
    aceptar = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Acepto")]'))
    )
    aceptar.click()
    print("✔ Cookies aceptadas")
except:
    print("❕ No apareció el banner de cookies.")

# Paso 3: Escribir "ciencia de datos" y hacer búsqueda
try:
    campo_busqueda = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Cargo o categoría"]')))
    campo_busqueda.clear()
    campo_busqueda.send_keys("ciencia de datos")
    campo_busqueda.send_keys(Keys.ENTER)
    print("🔍 Búsqueda enviada (con ENTER)")
except Exception as e:
    print("❌ Error en búsqueda:", type(e).__name__, e)
    driver.quit()
    exit()

# Paso 4: Cerrar popup de notificaciones si aparece
try:
    time.sleep(3)
    popup_btn = driver.find_element(By.XPATH, '//button[contains(text(),"Ahora no")]')
    popup_btn.click()
    print("✅ Popup cerrado")
except:
    print("❕ No apareció popup de notificaciones")

# Paso 5: Extraer info de ofertas
ofertas_extraidas = []

try:
    # 🟡 CAMBIO AQUÍ: Usamos "box_offer" en lugar de "bRS"
    tarjetas = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "box_offer")))
    print(f"\n🟡 Se encontraron {len(tarjetas)} ofertas en la primera página.\n")

    for tarjeta in tarjetas:
        try:
            try:
                titulo = tarjeta.find_element(By.CLASS_NAME, "js-o-link").text
            except:
                titulo = "No especificado"

            try:
                empresa = tarjeta.find_element(By.CLASS_NAME, "dNm").text
            except:
                empresa = "No especificado"

            try:
                ubicacion = tarjeta.find_element(By.CLASS_NAME, "dis-block").text
            except:
                ubicacion = "No especificado"

            try:
                link = tarjeta.find_element(By.CLASS_NAME, "js-o-link").get_attribute("href")
            except:
                link = "No especificado"

            ofertas_extraidas.append({
                "titulo": titulo,
                "empresa": empresa,
                "ubicacion": ubicacion,
                "link": link
            })

            print(f"Título: {titulo}\nEmpresa: {empresa}\nUbicación: {ubicacion}\nLink: {link}\n{'-'*40}")
            time.sleep(random.uniform(1.0, 1.8))
        except Exception as e:
            print("⚠ Error general al procesar una oferta:", e)

except Exception as e:
    print("❌ Error al cargar ofertas:", type(e).__name__, e)

# Paso 6: Guardar CSV
if ofertas_extraidas:
    with open("ofertas_ciencia_datos_colombia.csv", "w", newline='', encoding="utf-8") as archivo:
        campos = ofertas_extraidas[0].keys()
        writer = csv.DictWriter(archivo, fieldnames=campos)
        writer.writeheader()
        writer.writerows(ofertas_extraidas)
    print("\n✅ Ofertas guardadas en 'ofertas_ciencia_datos_colombia.csv'")
else:
    print("\n⚠ No se extrajo ninguna oferta.")

# Cerrar driver
driver.quit()
