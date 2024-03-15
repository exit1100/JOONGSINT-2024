
from flask import Blueprint, render_template, request, session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
import time, re
from config import Facebook_ID, Facebook_PW, host,port,user,password,db
import pymysql
import os
import json
from module.db_module import init, insert, get_setting

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
                print(self.driver_path)
                # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                driver.get(url)
                time.sleep(5)
                self.login_facebook(driver, url, login_name, login_pw)
                time.sleep(5)


                try:
                    img_text = re.findall(r'mount_0_0_[a-zA-Z0-9_\-]{2}', str(driver.page_source))
                    img_text = img_text[0]
                    print(img_text)
                except:
                    img_text = None
                    

                try:

                    profile_img = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, f"#{img_text} > div > div:nth-child(1) > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div > div.x78zum5.xdt5ytf.x1t2pt76.x1n2onr6.x1ja2u2z.x10cihs4 > div.x78zum5.xdt5ytf.x1t2pt76 > div > div > div:nth-child(1) > div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.x2lah0s.xl56j7k.x1qjc9v5.xozqiw3.x1q0g3np.x1l90r2v.x1ve1bff > div > div > div > div.x15sbx0n.x1xy773u.x390vds.xb2vh1x.x14xzxk9.x18u1y24.xs6kywh.x5wy4b0 > div > a > div > svg > g > image")))

                    profile_img = profile_img.get_attribute('xlink:href')
                    profile_img = profile_img

                    
                except:
                    profile_img = img_text

                try:
                    name = driver.find_element(By.CSS_SELECTOR, f'#{img_text} > div > div:nth-child(1) > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div > div.x78zum5.xdt5ytf.x1t2pt76.x1n2onr6.x1ja2u2z.x10cihs4 > div.x78zum5.xdt5ytf.x1t2pt76 > div > div > div:nth-child(1) > div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.x2lah0s.xl56j7k.x1qjc9v5.xozqiw3.x1q0g3np.x1l90r2v.x1ve1bff > div > div > div > div.x78zum5.x15sbx0n.x5oxk1f.x1jxijyj.xym1h4x.xuy2c7u.x1ltux0g.xc9uqle > div > div > div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x2lah0s.x193iq5w.x6s0dn4.xexx8yu > div > div > span > h1')
                    name = name.text
                except:
                    name = 'None'

                try:
                    about = driver.find_element(By.CSS_SELECTOR,f'#{img_text} > div > div:nth-child(1) > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div > div.x78zum5.xdt5ytf.x1t2pt76.x1n2onr6.x1ja2u2z.x10cihs4 > div.x78zum5.xdt5ytf.x1t2pt76 > div > div > div.x6s0dn4.x78zum5.xdt5ytf.x193iq5w > div.x9f619.x193iq5w.x1talbiv.x1sltb1f.x3fxtfs.x1swvt13.x1pi30zi.xw7yly9 > div > div.x9f619.x1n2onr6.x1ja2u2z.xeuugli.xs83m0k.x1xmf6yo.x1emribx.x1e56ztr.x1i64zmx.xjl7jj.xnp8db0.x1d1medc.x7ep2pv.x1xzczws > div.x7wzq59 > div > div:nth-child(1) > div > div > div > div > div.xieb3on > div:nth-child(1) > div > div > span')
                    about = about.text
                    # about = driver.find_element(By.CSS_SELECTOR,'#bio  > div')
                    # about = about.text.encode('utf-8').decode('utf-8')
                except:
                    about = 'aboutNone'

                try:
                    about_data = self.get_facebook_about(driver, self.username, login_name, login_pw)
                except:
                    about_data = {'detail' : 'a'}

                try:
                    profile_data = {
                        'sns' : 'facebook',
                        'name': name,
                        'about': about,
                        'profile_img': profile_img,
                        'detail': about_data['detail'],
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

                img_text = re.findall(r'mount_0_0_[a-zA-Z0-9_\-]{2}', str(driver.page_source))
                img_text = img_text[0]
                
                try:
                    contact = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#{img_text} > div > div:nth-child(1) > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div > div.x78zum5.xdt5ytf.x1t2pt76.x1n2onr6.x1ja2u2z.x10cihs4 > div.x78zum5.xdt5ytf.x1t2pt76 > div > div > div.x6s0dn4.x78zum5.xdt5ytf.x193iq5w > div > div > div > div:nth-child(1) > div > div > div > div > div.x1iyjqo2 > div > div')))
                    contact = contact.text
                except:
                    contact = '1'
                    
         

                    
                try:
                    about_data = {
                        'detail': contact,
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
    input_db = init(host,port,user,password,db)
    input_user = 	session['login_user']

    find_name = get_setting(input_db,'search_ID',input_user)
    
    # find_name = request.cookies.get("NAME")
    print(find_name)

    scraper = SNSProfileScraper(find_name , driver_path)
    facebook_profile = scraper.scrape_facebook_profile(Facebook_ID,Facebook_PW)

    result ={}

    result['facebook'] = facebook_profile



    # DB INSERT
    moduel = "facebook"
    type = "enterprice"
    json_result = json.dumps(facebook_profile)
    print("json_result: ", json_result)
    
    input_db = init(host,port,user,password,db)
    insert(input_db, moduel, type, json_result, input_user)
    
    
    return render_template("facebook_result.html", result=result)
