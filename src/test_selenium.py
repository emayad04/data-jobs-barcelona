from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--headless")  # Quita esta línea si quieres ver el navegador
options.add_argument("--disable-blink-features=AutomationControlled")

# Ruta al chromedriver
service = Service("./src/chromedriver.exe")


driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.google.com")
time.sleep(3)

print("Título de la página:", driver.title)

driver.quit()
