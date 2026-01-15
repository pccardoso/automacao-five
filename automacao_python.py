from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import os


EMAIL = "user"
SENHA = "password"

# URL DE LOGIN DA PLATAFORMA DESEJADA
URL_LOGIN = "https://exemple.com.br"

# URL ONDE FICAM OS CONTRATOS A SER BAIXADOS
URL_CONTRATOS = "https://exemple.com.br"

# DIRETÓRIO ONDE OS CONTRATOS SERÃO SALVOS
PASTA_DOWNLOAD = "/home/paulo-cesar/Documentos/contrato"

# PÁGINAÇÃO INICIAL
PAGINA_INICIAL = 55  # por exemplo, começar da página 18

os.makedirs(PASTA_DOWNLOAD, exist_ok=True)


# CONFIGURAÇÕES DO GOOGLE CHROME
options = webdriver.ChromeOptions()

prefs = {
    "download.default_directory": PASTA_DOWNLOAD,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True,
    "safebrowsing.enabled": True
}

options.add_experimental_option("prefs", prefs)
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)

# FUNÇÕES BÁSICAS
def esperar_download(pasta, timeout=180):
    tempo = 0
    while tempo < timeout:
        arquivos = os.listdir(pasta)
        if any(a.endswith(".crdownload") for a in arquivos):
            time.sleep(1)
            tempo += 1
        else:
            return
    print("⚠️ Timeout aguardando download")


def esperar_elemento(css_selector):
    """Espera indefinidamente até o elemento aparecer"""
    while True:
        try:
            el = driver.find_element(By.CSS_SELECTOR, css_selector)
            return el
        except:
            print(f"⏳ Aguardando elemento '{css_selector}'...")
            time.sleep(2)


def selecionar_200_por_pagina():
    """Seleciona 200 registros por página no DataTable"""
    while True:
        try:
            select = driver.find_element(By.CSS_SELECTOR, "div.dataTables_length select")
            options = [o.get_attribute("value") for o in select.find_elements(By.TAG_NAME, "option")]
            if "200" in options:
                Select(select).select_by_value("200")
                print("✅ Selecionado 200 por página")
                time.sleep(5)  # espera o DataTable atualizar
                return
            else:
                print("⏳ Aguardando opção '200' no select...")
                time.sleep(1)
        except:
            print("⏳ Aguardando select de quantidade...")
            time.sleep(1)


def baixar_contratos_pagina():
    links = []
    # espera os links aparecerem
    while not links:
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='baixar-contrato']")
        if not links:
            print("⏳ Aguardando links de contratos...")
            time.sleep(2)

    hrefs = [link.get_attribute("href") for link in links]
    print(f"🔗 {len(hrefs)} contratos encontrados")

    for i, href in enumerate(hrefs, start=1):
        print(f"⬇️  Baixando contrato {i}")
        driver.get(href)
        esperar_download(PASTA_DOWNLOAD)
        time.sleep(1)


def existe_proxima_pagina():
    try:
        driver.find_element(By.CSS_SELECTOR, "li.paginate_button.next:not(.disabled)")
        return True
    except:
        return False


def ir_proxima_pagina():
    botao = esperar_elemento("li.paginate_button.next:not(.disabled) a")
    driver.execute_script("arguments[0].click();", botao)
    time.sleep(3)


print("🔐 Login...")
driver.get(URL_LOGIN)

while True:
    try:
        driver.find_element(By.NAME, "email").send_keys(EMAIL)
        driver.find_element(By.NAME, "password").send_keys(SENHA)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        break
    except:
        print("⏳ Aguardando login...")
        time.sleep(2)

print("✅ Login confirmado")

driver.get(URL_CONTRATOS)

esperar_elemento("table")
print("✅ DataTable carregada")

selecionar_200_por_pagina()

pagina = 1
while pagina < PAGINA_INICIAL:
    if existe_proxima_pagina():
        ir_proxima_pagina()
        pagina += 1
        esperar_elemento("table")
        print(f"⏩ Pulando para página {pagina}")
    else:
        print("⚠️ Página inicial configurada maior que o total de páginas")
        break

print(f"\n📄 Baixando a página {pagina}...")
baixar_contratos_pagina()


driver.quit()
print("🏁 Script finalizado com sucesso")
