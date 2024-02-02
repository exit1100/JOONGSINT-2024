
from flask import Blueprint, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time, re
from config import Facebook_ID, Facebook_PW

facebook_module = Blueprint("facebook_module", __name__)

@facebook_module.route("/facebook_result", methods=["POST"])
def facebook_result():
    class SNSProfileScraper:
        def __init__(self, username , driver_path):
            self.driver_path = driver_path
            self.username = username

        def login_facebook(self, driver, target_url, login_name, login_pw):
            fb_url = 'https://mobile.facebook.com/'

            driver.implicitly_wait(10)
            driver.get(fb_url)
            time.sleep(3)

            username_input = driver.find_element(By.CSS_SELECTOR, "input[name='email']")
            password_input = driver.find_element(By.CSS_SELECTOR, "input[name='pass']")

            username_input.send_keys(login_name)
            password_input.send_keys(login_pw)

            login_button = driver.find_element(By.XPATH , "//button[@type='button']")
            login_button.click()

            print('페이스북 로그인')
            time.sleep(3)
            driver.get(target_url)
            time.sleep(3)
            print('페이스북 진입성공')
        
        def scrape_facebook_profile(self , login_name, login_pw):
            try:
                url = 'https://mobile.facebook.com/' + self.username
                options = webdriver.ChromeOptions()
                options.add_argument('headless')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                options.add_argument('--lang=ko_KR.UTF-8')
                driver = webdriver.Chrome(executable_path=self.driver_path, options=options)
                driver.get(url)
                time.sleep(5)
                self.login_facebook(driver, url, login_name, login_pw)
                time.sleep(5)
                try:
                    name = driver.find_element(By.CSS_SELECTOR,'#cover-name-root > h3')
                    name = name.text
                except:
                    name = 'None'

                try:
                    element_present = EC.presence_of_element_located((By.CSS_SELECTOR, '#bio  > div'))
                    WebDriverWait(driver, 10).until(element_present)
                    about = driver.find_element(By.CSS_SELECTOR,'#bio  > div')
                    about = about.text
                    # about = driver.find_element(By.CSS_SELECTOR,'#bio  > div')
                    # about = about.text.encode('utf-8').decode('utf-8')
                except:
                    about = 'aboutNone'

                try:
                    img_text = re.findall(r'u_0_u_[a-zA-Z0-9_\-]{2}', str(driver.page_source))
                    img_text = img_text[0]
                except:
                    img_text = None

                try:
                    profile_img = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR , f'#{img_text} > a > div > i')))
                    profile_img = profile_img.get_attribute('style')
                    pattern = r"url\(['\"]?([^'\")]+)['\"]?\)"
                    match = re.search(pattern, profile_img)
                    profile_img = match.group(1)
                        
                    # profile_img = profile_img.split('background:')[1].split(';')[0].strip()
                    # profile_img = profile_img.replace('url(\'', '').replace('\')', '')
                    

                except:
                    profile_img = img_text

                try:
                    about_data = self.get_facebook_about(driver, self.username, login_name, login_pw)
                except:
                    about_data = {'contact' : 'a',  'birth': 'b', 'career': 'b'}

                try:
                    profile_data = {
                        'sns' : 'facebook',
                        'name': name,
                        'about': about,
                        'profile_img': profile_img,
                        'contact': about_data['contact'],
                        'birth': about_data['birth'],
                        'career':about_data['career'],
                    }
                    return profile_data
                except:
                    return None
            except:
                return None
            
        def get_facebook_about(self, driver, username, login_name, login_pw):
            try:
                url = 'https://mobile.facebook.com/' + username + '/about'
                options = webdriver.ChromeOptions()
                options.add_argument('headless')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                options.add_argument('--lang=ko_KR.UTF-8')
                driver = webdriver.Chrome(executable_path=self.driver_path, options=options)
                driver.get(url)
                time.sleep(5)
                self.login_facebook(driver, url, login_name, login_pw)
                time.sleep(5)
                
                try:
                    element_present = EC.presence_of_element_located((By.CSS_SELECTOR, '#contact-info'))
                    WebDriverWait(driver, 10).until(element_present)
                    contact = driver.find_element(By.CSS_SELECTOR,'#contact-info')
                    contact = contact.text
                except:
                    contact = '1'
                    
                try:
                    element_present = EC.presence_of_element_located((By.CSS_SELECTOR, '#basic-info > div > div:nth-of-type(1) > div > div._5cdv.r'))
                    WebDriverWait(driver, 10).until(element_present)
                    birth = driver.find_element(By.CSS_SELECTOR,'#basic-info > div > div:nth-of-type(1) > div > div._5cdv.r')
                    birth = birth.text
                except:
                    birth = '2'
                    
                try:
                    element_present = EC.presence_of_element_located((By.CSS_SELECTOR, '#work > div > div > div > div'))
                    WebDriverWait(driver, 10).until(element_present)
                    career = driver.find_element(By.CSS_SELECTOR,'#work > div > div > div > div')
                    career = career.text
                except:
                    career = '3'

                    
                try:
                    about_data = {
                        'contact': contact,
                        'birth': birth,
                        'career': career,
                    }

                    #크롤링 파일 저장 코드

                    # filename = url[url.find('//')+3:]
                    # filename = filename.replace('/','_')
                    # f = open(filename+'.html','w', encoding='utf-8')
                    # f.write(str(driver.page_source))
                    # f.close()
                    #print(driver.page_source)
                    return about_data
                except:
                    return None
            except:
                return None

    
    
    driver_path = 'app/chromedriver.exe'

    find_name = request.cookies.get("NAME")

    scraper = SNSProfileScraper(find_name , driver_path)
    facebook_profile = scraper.scrape_facebook_profile(Facebook_ID,Facebook_PW)

    result ={}

    result['facebook'] = facebook_profile
    
    return render_template("facebook_result.html", result=result)