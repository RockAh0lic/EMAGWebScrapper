
# import module
from operator import imod
from numpy import prod
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv
import msvcrt as m
import sqlite3

f = open('ArticoleExtrase.csv',
        'w', newline='', encoding="utf-8")
writer = csv.writer(f)
header = ['Categorie', 'Denumire Produs', 'Link']
writer.writerow(header)

con = sqlite3.connect('ArticoleExtrase.db')
cur = con.cursor()
try:
    cur.execute('''CREATE TABLE aricole
                (Denumire, Link, Categorie)''')
    con.commit()
except:
    print('Baza de date exista deja')

produse = []

driver = webdriver.Chrome(
    'chromedriver_win32\chromedriver.exe')

class Articol:
    def __init__(self, produs, categorie, link):
        self.produs = produs
        self.link = link
        self.categorie = categorie

class Links:
    def __init__(self, link, categorie):
        self.link = link
        self.categorie = categorie

def goHome():
    driver.get("https://www.emag.ro/")
    driver.implicitly_wait(0.5)
    mainWindow = driver.current_window_handle

def goTo(pageURL):
    driver.get(pageURL)
    driver.implicitly_wait(0.5)

def getLabeledLinks():
    links = []

    sectiuni = driver.find_elements(
        By.CLASS_NAME, "megamenu-list-department__department-name")

    j = len(sectiuni)

    for i in range(1, j):
        hover = ActionChains(driver).move_to_element(sectiuni[i])
        hover.perform()
        time.sleep(0.1)

    coloane = driver.find_elements(
        By.CLASS_NAME, "megamenu-column")

    for k in range(1, len(coloane)):
        linkuri = driver.find_elements(
            By.CLASS_NAME, "megamenu-item")

    for l in range(len(linkuri)):
        link_html = linkuri[l].get_attribute('innerHTML')
        if(link_html.find('class="label ') != -1):
            l = linkuri[l].get_attribute('href')
            if(link_html.find('Nou') != -1):
                categorie = 'Nou'
            elif(link_html.find('Info') != -1):
                categorie = 'Info'
            else:
                categorie = 'Promo'
            if(l is None):
                continue
            else:
                obj = Links(l, categorie)
                links.append(obj)
    return links

def checkItemListPage():
    items = driver.find_elements(By.CLASS_NAME, "js-products-container")
    if (len(items) > 0):
        return 1
    else:
        return 0

def addProductsToList(elementeProduse):
    for j in range(len(elementeProduse)):
        Produs = elementeProduse[j].find_element(By.XPATH, '..')
        NbOfParentsToMainElement = 6
        while(NbOfParentsToMainElement):
            Produs = Produs.find_element(By.XPATH, '..')
            NbOfParentsToMainElement -= 1
        numeProdus = Produs.get_attribute('data-name')
        linkProdus = Produs.find_element(
            By.TAG_NAME, 'a').get_attribute('href')
        categorieProdus = elementeProduse[j].get_attribute('innerHTML')
        if(linkProdus != 'javascript:;'):
            obj = Articol(numeProdus, categorieProdus, linkProdus)
            ok = True
            
            #Eliminare duplicate
            for k in range(len(produse)):
                if(produse[k].link == obj.link):
                    ok = False
                    produse[k].categorie += ", " + obj.categorie
                    break
            
            if(ok == True):
                try:
                    #Add To Favourites
                    addToFavBtn = Produs.find_element(By.CLASS_NAME, "add-to-favorites")
                    click = ActionChains(driver).click(addToFavBtn)
                    click.perform()
                except:
                    continue
                #Add object to array
                produse.append(obj)

def goThroughLinks(links):
    for i in range(len(links)):
        goTo(links[i].link)
        time.sleep(1)
        if(checkItemListPage()):
            elementeProduse = driver.find_elements(By.CLASS_NAME, "extra-badge") #Promovat
            addProductsToList(elementeProduse)
            elementeProduse = driver.find_elements(By.CLASS_NAME, "badge") #Stock Busters, Top Favorite si Super Pret
            addProductsToList(elementeProduse)
            try:
                secondPageBtnLink = driver.find_element(By.CLASS_NAME, 'js-change-page').get_attribute('href')
                goTo(secondPageBtnLink)
                elementeProduse = driver.find_elements(By.CLASS_NAME, "extra-badge") #Promovat
                addProductsToList(elementeProduse)
                elementeProduse = driver.find_elements(By.CLASS_NAME, "badge") #Stock Busters, Top Favorite si Super Pret
                addProductsToList(elementeProduse)
            except:
                continue

    for j in range(len(produse)):
        obj = produse[j]
        row = [obj.categorie, obj.produs, obj.link]
        writer.writerow(row)
    f.close()

def addArticlesToDB():
    for i in range(len(produse)):
        try:
            insertQuery = "INSERT INTO aricole VALUES ('" + str(produse[i].produs) + "','" + str(produse[i].link) + "','" + str(produse[i].categorie) + "')"
            cur.execute(str(insertQuery))
        except:
            continue
    con.commit()
    for row in cur.execute('SELECT * FROM aricole ORDER BY Denumire'):
        try:
            print(row)
        except:
            continue
    con.close()

def wait():
    m.getch()

def detectCaptch():
    time.sleep(20)
    try:
        driver.find_element(By.CLASS_NAME, 'challenge-container')
        wait()
    except:
        return

def auth():
    email = input('Enter eMag account eMail address:\n')
    passwd = input('Type the password for the account:\n')
    try:
        userBtn = driver.find_element(By.CLASS_NAME, 'btn-emag')
        click = ActionChains(driver).click(userBtn)
        click.perform()
        emailField = driver.find_element(By.ID, 'user_login_email')
        emailField.send_keys(email)
        continueBtn = driver.find_element(By.ID, 'user_login_continue')
        click = ActionChains(driver).click(continueBtn)
        click.perform()
        detectCaptch()
        passwdField = driver.find_element(By.ID, 'user_login_password')
        passwdField.send_keys(passwd)
        continueBtn = driver.find_element(By.ID, 'user_login_continue')
        click = ActionChains(driver).click(continueBtn)
        click.perform()
        detectCaptch()
        try:
            activateLater =driver.find_element(By.CLASS_NAME, 'btn-default')
            click = ActionChains(driver).click(activateLater)
            click.perform()
        except:
            goHome()
            return
        goHome()
    except:
        goHome()
        return
    time.sleep(5)

goHome()
#comment line below to skip auth
authBool = input('Do you want to login? y/n \n')
if(authBool == 'y'):
    auth()
links = getLabeledLinks()
goThroughLinks(links)
addArticlesToDB()
driver.quit()
