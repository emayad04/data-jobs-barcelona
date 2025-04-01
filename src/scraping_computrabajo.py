from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import csv
import random
import os
import re

# Configuración del navegador
options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

service = ChromeService(executable_path="./src/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

driver.get("https://co.computrabajo.com")

# Aceptar cookies
try:
    aceptar = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Acepto")]'))
    )
    aceptar.click()
    print("✔ Cookies aceptadas")
except:
    print("❕ No apareció el banner de cookies.")

# Buscar "ciencia de datos"
try:
    campo_busqueda = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Cargo o categoría"]')))
    campo_busqueda.clear()
    campo_busqueda.send_keys("data sciencie")
    campo_busqueda.send_keys(Keys.ENTER)
    print("🔍 Búsqueda enviada (con ENTER)")
except Exception as e:
    print("❌ Error en búsqueda:", type(e).__name__, e)
    driver.quit()
    exit()

# Cerrar popup de notificaciones si aparece
try:
    time.sleep(3)
    popup_btn = driver.find_element(By.XPATH, '//button[contains(text(),"Ahora no")]')
    popup_btn.click()
    print("✅ Popup cerrado")
except:
    print("❕ No apareció popup de notificaciones")

# Extraer tarjetas de ofertas
ofertas_extraidas = []

try:
    tarjetas = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "box_offer")))
    print(f"\Se encontraron {len(tarjetas)} ofertas en la primera página.\n")

    for tarjeta in tarjetas:
        try:
            try:
                titulo = tarjeta.find_element(By.CLASS_NAME, "js-o-link").text
                link = tarjeta.find_element(By.CLASS_NAME, "js-o-link").get_attribute("href")
            except:
                titulo, link = "No especificado", "No especificado"

            try:
                empresa_ubicacion = tarjeta.find_element(By.CLASS_NAME, "fs16").text.split("\n")
                empresa = empresa_ubicacion[1] if len(empresa_ubicacion) > 1 else "No especificado"
                ubicacion = empresa_ubicacion[2] if len(empresa_ubicacion) > 2 else "No especificado"
            except:
                empresa, ubicacion = "No especificado", "No especificado"

            # 🔽 Entrar al detalle de la oferta
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(link)
            time.sleep(2)

            try:
                salario = driver.find_element(By.XPATH, '//span[contains(text(),"$")]').text
            except:
                salario = "No especificado"

            try:
                tipo_contrato = driver.find_element(By.XPATH, '//span[contains(text(),"Contrato")]').text
            except:
                tipo_contrato = "No especificado"

            try:
                modalidad = driver.find_element(By.XPATH, '//span[contains(text(),"Presencial") or contains(text(),"Remoto") or contains(text(),"Híbrido")]').text
            except:
                modalidad = "No especificado"

            try:
                descripcion = driver.find_element(By.CLASS_NAME, "box_detail").text
                requisitos = "\n".join([line.strip() for line in descripcion.splitlines() if "requisito" in line.lower() or "requerim" in line.lower()])
                if not requisitos:
                    requisitos = "No especificado"
            except:
                requisitos = "No especificado"

            # 🔍 Fecha de publicación
            try:
                texto_fecha = driver.find_element(By.XPATH, '//p[contains(text(),"Hace")]').text
                match = re.search(r"Hace (\d+) día", texto_fecha)
                if match:
                    dias = int(match.group(1))
                    fecha_publicacion = (datetime.today() - timedelta(days=dias)).strftime("%Y-%m-%d")
                else:
                    fecha_publicacion = "No especificado"
            except:
                fecha_publicacion = "No especificado"

            # Cerrar pestaña del detalle
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            # Guardar la oferta
            ofertas_extraidas.append({
                "titulo": titulo,
                "empresa": empresa,
                "ubicacion": ubicacion,
                "link": link,
                "salario": salario,
                "tipo_contrato": tipo_contrato,
                "modalidad": modalidad,
                "requisitos": requisitos,
                "fecha_publicacion": fecha_publicacion
            })

            print(f"✅ {titulo}\nEmpresa: {empresa}\nUbicación: {ubicacion}\nContrato: {tipo_contrato}\nModalidad: {modalidad}\nSalario: {salario}\nFecha: {fecha_publicacion}\nLink: {link}\n{'-'*60}")
            time.sleep(random.uniform(1.0, 1.5))

        except Exception as e:
            print("⚠ Error al procesar una oferta:", e)

except Exception as e:
    print("❌ Error al cargar ofertas:", type(e).__name__, e)

# Guardar CSV
output_path = "./data-jobs-colombia/src/dataset/ofertas_ciencia_datos_colombia.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

if ofertas_extraidas:
    with open(output_path, "w", newline='', encoding="utf-8") as archivo:
        campos = ofertas_extraidas[0].keys()
        writer = csv.DictWriter(archivo, fieldnames=campos)
        writer.writeheader()
        writer.writerows(ofertas_extraidas)
    print(f"\n✅ Ofertas guardadas en '{output_path}'")
else:
    print("\n⚠ No se extrajo ninguna oferta.")

driver.quit()