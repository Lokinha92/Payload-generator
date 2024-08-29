from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
import time

class PicPayMonitor:
    def __init__(self, driver_path, url):
        self.driver_path = driver_path
        self.url = url
        self.service = Service(executable_path=self.driver_path)
        self.driver = webdriver.Edge(service=self.service)
        self.intervalo = 4  # Intervalo de atualização em segundos

    def iniciar_navegador(self):
        self.driver.get(self.url)
        print("A página exibiu um código de confirmação. Insira o código no aplicativo do seu celular.")
        input("Pressione Enter quando o redirecionamento ocorrer...")
        
    def acessar_painel(self):
        try:
            painel = self.driver.find_element(By.XPATH, '//div[@id="mat-tab-label-0-1"]')
            painel.click()
            print("Botão inicial clicado com sucesso!")
            time.sleep(3)
        except Exception as e:
            print(f"Erro ao encontrar o botão inicial: {e}")

    def obter_valor_ultima_transacao(self):
        try:
            tabela = self.driver.find_element(By.XPATH, '//table')
            linhas = tabela.find_elements(By.TAG_NAME, 'tr')

            if len(linhas) > 1:
                primeira_linha = linhas[1]
                
                quarta_coluna = primeira_linha.find_elements(By.TAG_NAME, 'td')[4]
                
                valor_transacao = quarta_coluna.text
                return valor_transacao
            else:
                print("Tabela ainda não está pronta. Tentando novamente...")
                return None
        except Exception as e:
            print(f"Erro ao acessar o valor da última transação: {e}")
            return None
        
    def obter_id_ultima_transacao(self):
        try:
            tabela = self.driver.find_element(By.XPATH, '//table')
            linhas = tabela.find_elements(By.TAG_NAME, 'tr')

            if len(linhas) > 1:
                primeira_linha = linhas[1]
                
                primeira_coluna = primeira_linha.find_elements(By.TAG_NAME, 'td')[1]
                
                id = primeira_coluna.text
                id = id.split('#')[1]
                return id
            else:
                print("Tabela ainda não está pronta. Tentando novamente...")
                return None
        except Exception as e:
            print(f"Erro ao acessar o valor da última transação: {e}")
            return None
        

    def atualizar_pagina(self):
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, 'i.fa.fa-undo')
            element.click()
            print("Página atualizada com sucesso!")
        except Exception as e:
            print(f"Erro ao tentar atualizar a página: {e}")

    def monitorar_transacoes(self):
        while True:
            valor = self.obter_valor_ultima_transacao()
            id = self.obter_id_ultima_transacao()
            if valor:
                print(f"Valor da última transação: {valor}")
                print(f"ID: {id}")
            time.sleep(self.intervalo)
            self.atualizar_pagina()

    def fechar_navegador(self):
        self.driver.quit()
        print("Navegador fechado.")