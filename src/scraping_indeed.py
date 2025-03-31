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
    campo_busqueda.send_keys("ciencia de datos")
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
    print(f"\n🟡 Se encontraron {len(tarjetas)} ofertas en la primera página.\n")

    for tarjeta in tarjetas:
        try:
            titulo = tarjeta.find_element(By.CLASS_NAME, "js-o-link").text
            link = tarjeta.find_element(By.CLASS_NAME, "js-o-link").get_attribute("href")
            empresa = tarjeta.find_element(By.CLASS_NAME, "dNm").text if tarjeta.find_elements(By.CLASS_NAME, "dNm") else "No especificado"
            ubicacion = tarjeta.find_element(By.CLASS_NAME, "dis-block").text if tarjeta.find_elements(By.CLASS_NAME, "dis-block") else "No especificado"

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
                habilidades = "\n".join([line.strip() for line in descripcion.splitlines() if "Habilidad" in line or "Conocimiento" in line])
            except:
                habilidades = "No especificado"

            # Cerrar la pestaña del detalle
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
                "habilidades": habilidades
            })

            print(f"✅ {titulo}\nEmpresa: {empresa}\nUbicación: {ubicacion}\nContrato: {tipo_contrato}\nModalidad: {modalidad}\nSalario: {salario}\nLink: {link}\n{'-'*60}")
            time.sleep(random.uniform(1.0, 1.5))

        except Exception as e:
            print("⚠ Error al procesar una oferta:", e)

except Exception as e:
    print("❌ Error al cargar ofertas:", type(e).__name__, e)

# Guardar CSV
if ofertas_extraidas:
    with open("ofertas_ciencia_datos_colombia.csv", "w", newline='', encoding="utf-8") as archivo:
        campos = ofertas_extraidas[0].keys()
        writer = csv.DictWriter(archivo, fieldnames=campos)
        writer.writeheader()
        writer.writerows(ofertas_extraidas)
    print("\n✅ Ofertas guardadas en 'ofertas_ciencia_datos_colombia.csv'")
else:
    print("\n⚠ No se extrajo ninguna oferta.")

driver.quit()
