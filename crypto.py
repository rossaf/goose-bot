from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
import time
from dotenv import load_dotenv
import os

def loadBrowser():
    load_dotenv()
    CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
    GOOGLE_CHROME_PATH = os.getenv("GOOGLE_CHROME_PATH")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.binary_location = GOOGLE_CHROME_PATH

    browser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
    return browser


def getCrypto(args):
    
    if args[0] == 'get':
        if len(args) == 4:
            return getPrice(args[1], args[2], args[3])
        elif len(args) == 3:
            return getPrice(args[1], args[2], '3M')
        elif len(args) == 2:
            return getPrice(args[1], 'USD', '3M')
        else:
            return ["**ERROR:** _You are missing an asset... (Ex. BTC, ETH, LTC)_", "**FORMAT:** _!coin get {asset} {compare} {period}_"]
    elif args[0] == 'top':
        return getTop()
    else:
       return ["**ERROR:** _Unrecognized command (Try using !help)_"]


def getPrice(coin, compare, period):
    coin = coin.upper()
    browser = loadBrowser()

    link = f'cryptowat.ch/charts/KRAKEN:{coin}-{compare}'
    if period:
        link = link + f'?period={period}'
        
    print(link)
    with browser as driver:        
        desktop = {'output': str(link) + '-desktop.png', 'width': 2916, 'height': 844}
        
        linkWithProtocol = 'https://' + str(link)
        
        
        driver.set_window_size(desktop['width'], desktop['height'])
        driver.get(linkWithProtocol)

        time.sleep(2)
        driver.save_screenshot('temp.png')
        try:    
            price = driver.find_element(By.XPATH, '//*[@id="marketview-watchlist"]/div/div/nav/div[4]/a/div[2]/span[1]')
            change = driver.find_element(By.XPATH, '//*[@id="marketview-watchlist"]/div/div/nav/div[4]/a/div[2]/span[2]/span')
            ele = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[1]/div[2]/div/div[1]/div/div/div[3]/div[1]')
        except:
            return ['**ERROR:** There was an error serving your request...']
        loc = ele.location
        size = ele.size
        pricein = price.get_attribute("innerHTML")
        changein = change.get_attribute("innerHTML")
        x = loc['x']
        y = loc['y']
        w = size['width']
        h = size['height']
        width = x + w
        height = y + h
        im = Image.open('temp.png')
        im = im.crop((int(x), int(y), int(width), int(height)))
        im.save('temp.png')
        

        return [f'**{coin}/{compare} Prices {period}:**', f'${pricein}/{changein}', '~discord.File("temp.png")']

def getTop():
    link = 'cryptowat.ch/assets'
    browser = loadBrowser()

    with browser as driver:
        desktop = {'output': str(link) + '-desktop.png', 'width': 1920, 'height': 1080}
            
        linkWithProtocol = 'https://' + str(link)
            
            
        driver.set_window_size(desktop['width'], desktop['height'])
        driver.get(linkWithProtocol)

        time.sleep(2)
        driver.save_screenshot('temp.png')
        try: 
            ele = driver.find_element(By.XPATH, '//*[@id="main-content"]/div[1]/div/div/div[3]')
        except:
            return ['**ERROR:** There was an error serving your request...']
        loc = ele.location
        size = ele.size
        x = loc['x']
        y = loc['y']
        w = size['width']
        h = 600
        width = x + w
        height = y + h
        im = Image.open('temp.png')
        im = im.crop((int(x), int(y), int(width), int(height)))
        im.save('temp.png')
        
        
    return ['**Top assets right now:**', '~discord.File("temp.png")']