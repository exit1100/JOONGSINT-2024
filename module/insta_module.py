
from flask import Blueprint, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time, re
from config import Instagram_ID ,Instagram_PW

insta_module = Blueprint("insta_module", __name__)

@insta_module.route("/insta_result", methods=["POST"])
def insta_result():
    class SNSProfileScraper:
        def __init__(self, username , driver_path):
            self.driver_path = driver_path
            self.username = username

        def login_instargram(self, driver, target_url, login_name, login_pw):
            insta_url = 'https://www.instagram.com'
            driver.implicitly_wait(10)
            driver.get(insta_url)
            time.sleep(3)

            username_input = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
            password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")

            username_input.send_keys(login_name)
            password_input.send_keys(login_pw)

            login_button = driver.find_element(By.XPATH , "//button[@type='submit']")
            login_button.click()

            print('인스타그램 로그인')
            time.sleep(3)
            driver.get(target_url)
            time.sleep(3)
            print('인스타그램 진입성공')



        def scrape_instagram_profile(self, login_name, login_pw):
            try:
                url = 'https://www.instagram.com/' + self.username
                options = webdriver.ChromeOptions()
                options.add_argument('headless')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                options.add_argument('--lang=ko_KR.UTF-8')
                driver = webdriver.Chrome(executable_path=self.driver_path, options=options)
                driver.get(url)
                time.sleep(5)
                self.login_instargram(driver, url, login_name, login_pw)
                time.sleep(5)


                # filename = url[url.find('//')+2:]
                # filename = filename.replace('/','_')
                # f = open(filename+'.html','w', encoding='utf-8')
                # f.write(str(driver.page_source))
                # f.close()

                try:
                    bio_text = re.findall(r'mount_0_0_[a-zA-Z0-9_\-]{2}', str(driver.page_source))
                    bio_text = bio_text[0]
                except:
                    bio_text = None




                try:
                    name = driver.find_element(By.TAG_NAME, 'title').get_attribute('textContent')
                    name = name.split('•')[0]
                except:
                    name = 'name'


                try:
                    bio = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, f"#{bio_text} > div > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div > div > div.x78zum5.xdt5ytf.x10cihs4.x1t2pt76.x1n2onr6.x1ja2u2z > div.x9f619.xnz67gz.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.x1q0g3np.xqjyukv.x1qjc9v5.x1oa3qoh.x1qughib > div.xh8yej3.x1gryazu.x10o80wk.x14k21rp.x1porb0y.x17snn68.x6osk4m > div:nth-child(2) > section > main > div > header > section > div._aa_c")))
                    
                    bio = bio.text
                except:
                    bio = bio_text

                try:
                    post = driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]')
                    post = post.get_attribute('content').split('-')[0]
                    # post = post.text
                except:
                    post = None

                try:
                    profile_img = driver.find_element(By.CSS_SELECTOR, 'meta[property="og:image"]')
                    profile_img = profile_img.get_attribute('content')
                except:
                    profile_img = 'profile_img'


                try:
                    profile_data = {
                        'sns' : 'instgram',
                        'name': name,
                        'bio': bio,
                        'post': post,
                        'profile_img': profile_img,
                    }

                    

                    return profile_data
                except Exception as e:
                    return e
            except:
                return '123'

    
    
    driver_path = 'app/chromedriver.exe'

    find_name = request.cookies.get("NAME")

    scraper = SNSProfileScraper(find_name , driver_path)
    instagram_profile = scraper.scrape_instagram_profile(Instagram_ID,Instagram_PW)

    result ={}

    result['instagram'] = instagram_profile
    
    return render_template("insta_result.html", result=result)