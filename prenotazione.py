from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType

from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from datetime import datetime
import traceback


import os

def set_viewport_size(driver, width, height):
    window_size = driver.execute_script("""
        return [window.outerWidth - window.innerWidth + arguments[0],
          window.outerHeight - window.innerHeight + arguments[1]];
        """, width, height)
    driver.set_window_size(*window_size)


opts = Options()
opts.headless = True

prenota_da = datetime.strptime('2021-6-27', '%Y-%m-%d')
prenota_a = datetime.strptime('2021-11-8', '%Y-%m-%d')

cf = 'CF'
tessera_sanitaria = '000000'
nome_prenotazione = ''
cognome_prenotazione = ''
email_prenotazione = ''

browser = Firefox(options=opts)
try:
    browser.get('https://vaccinicovid.regione.veneto.it/ulss8')

    set_viewport_size(browser, 1366, 1300)    
    
    # 58 Fiera vicenza
    # 60 Noventa
    # 62 Lonigo
    # 63 Valdagno marzotto
    # 323 Montecchio FIAMM
    # 59 Trissino
    
    btn_loc = None
    prenotato = False

    

    while not prenotato:
        trovato_luogo = False

        while not trovato_luogo:
            WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, "cod_fiscale"))
            )


            cod_fiscale = browser.find_element_by_id('cod_fiscale')
            cod_fiscale.send_keys(cf)
            num_tessera = browser.find_element_by_id('num_tessera')        
            num_tessera.send_keys(tessera_sanitaria)

            sleep(0.5)
            check = browser.find_element_by_xpath('//*[@id="corpo1"]/div[4]/div[2]/input')    
            action = webdriver.common.action_chains.ActionChains(browser)
            action.move_to_element(check)
            action.click()
            action.perform()

            btn = browser.find_element_by_xpath('//*[@id="corpo1"]/div[6]/div[2]/button')    
            btn.click()            
            btn_nati = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Nati dal 1962 al 2009')]"))
            )

            try:
                btn_nati.click()
                WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Montecchio FIAMM')]"))
                )

                results = browser.find_elements_by_css_selector('.btn.btn-full')
                for btn in results:
                    luogo = btn.get_attribute('innerHTML')
                    if btn.is_enabled():
                        print('Disponibile ' + luogo)

                    if btn.is_enabled() and ('Fiera' in luogo or 'Villa Berica' in luogo):
                        trovato_luogo = True
                        btn_loc = btn
            except:
                pass
            

            if not trovato_luogo:
                browser.refresh();
                sleep(1)            

        btn_loc.click()
        sleep(0.5)

        trovato = False
        tentativo = 1
        btn_giorno = None
        while not trovato and tentativo < 4:
            tentativo += 1 
            try:
                giorni = browser.find_elements_by_css_selector('.fc-day.highlight')            
                if len(giorni) == 0:
                    raise Exception('Giorni non trovati')
                for giorno in giorni:
                    if not trovato:
                        print(giorno.get_attribute('data-date'))                
                        date_time_str = giorno.get_attribute('data-date')
                        data = datetime.strptime(date_time_str, '%Y-%m-%d')                

                        if prenota_a >= data >= prenota_da:
                            print('data valida')
                            btn_giorno = giorno.find_element_by_xpath('.//a')                            
                            trovato = True                              
                        else:
                            print('data non buona')
                
            except Exception as e:    
                print('cambio mese')
                next = browser.find_element_by_css_selector('.fc-next-button')
                next.click()
                sleep(0.5)

        if btn_giorno:
            sleep(0.2)
            try:
                btn_giorno.click()
            except:
                sleep(0.2)
                btn_giorno.click()

            WebDriverWait(browser, 2).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Fasce disponibili')]"))
            )                    
            btn_orari = browser.find_elements_by_css_selector('.btn.btn-full')
            btn_orari[0].click()

            cognome = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.XPATH, '//input[@name="cognome"]'))
            )

            cognome.send_keys(cognome_prenotazione)
            nome = browser.find_element_by_xpath('//input[@name="nome"]')
            nome.send_keys(nome_prenotazione)
            email = browser.find_element_by_xpath('//input[@name="email"]')
            email.send_keys(email_prenotazione)

            sleep(0.2)
            conferma = WebDriverWait(browser, 5).until(
                EC.element_to_be_clickable((By.ID, 'bottoneconferma'))
            )
            conferma.click()


        if not trovato:
            print('Giorno compatibile non trovato')
            browser.refresh();
            sleep(1) 
        else:
            prenotato = True
            print('Prenotazione effettuata')
        
    
except Exception as err:    
    print(err)
    traceback.print_tb(err.__traceback__)
    print(browser.page_source)     

finally:
    browser.close()
    browser.quit()