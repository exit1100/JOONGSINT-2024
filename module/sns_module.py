
from flask import Blueprint, render_template, request
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time, re
from config import Instagram_ID ,Instagram_PW , Facebook_ID, Facebook_PW

sns_module = Blueprint("sns_module", __name__)

@sns_module.route("/sns_result", methods=["POST"])
def sns_result():
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
                    profile_img = driver.find_element(By.CSS_SELECTOR , f'#{img_text} > a > div > i')
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

        def scrape_twitter_profile(self):
            try:
                url = 'https://twitter.com/' + self.username
                options = webdriver.ChromeOptions()
                options.add_argument('headless')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                driver = webdriver.Chrome(executable_path=self.driver_path, options=options)
                driver.get(url)
                time.sleep(5)
                try:                
                    name = driver.find_element(By.CSS_SELECTOR , '#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div > div > div.css-1dbjc4n.r-aqfbo4.r-gtdqiz.r-1gn8etr.r-1g40b8q > div:nth-child(1) > div > div > div > div > div > div.css-1dbjc4n.r-16y2uox.r-1wbh5a2.r-1pi2tsx.r-1777fci > div > h2 > div > div > div > div > span.css-901oao.css-16my406.r-1awozwy.r-18jsvk2.r-6koalj.r-poiln3.r-b88u0q.r-bcqeeo.r-1udh08x.r-3s2u2q.r-qvutc0 > span > span:nth-child(1)')
                    name = name.text
                except:
                    name = None

                try:
                    screen_name = driver.find_element(By.CSS_SELECTOR , '#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div > div > div:nth-child(3) > div > div > div > div.css-1dbjc4n.r-1ifxtd0.r-ymttw5.r-ttdzmv > div.css-1dbjc4n.r-6gpygo.r-14gqq1x > div.css-1dbjc4n.r-1wbh5a2.r-dnmrzs.r-1ny4l3l > div > div.css-1dbjc4n.r-1awozwy.r-18u37iz.r-1wbh5a2 > div > div > div > span')
                    screen_name = screen_name.text
                except:
                    screen_name = 'None'

                try:
                    bio = driver.find_element(By.CSS_SELECTOR , '#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div > div > div:nth-child(3) > div > div > div > div.css-1dbjc4n.r-1ifxtd0.r-ymttw5.r-ttdzmv > div:nth-child(3) > div > div > span')
                    bio = bio.text
                except:
                    bio = None

                try:
                    location = driver.find_element(By.CSS_SELECTOR , '#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div > div > div:nth-child(3) > div > div > div > div.css-1dbjc4n.r-1ifxtd0.r-ymttw5.r-ttdzmv > div:nth-child(4) > div > span:nth-child(1) > span > span')
                    location = location.text
                except:
                    location = None

                try:
                    profile_img = driver.find_element(By.CSS_SELECTOR , '#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div > div > div:nth-child(3) > div > div > div > div.css-1dbjc4n.r-1ifxtd0.r-ymttw5.r-ttdzmv > div.css-1dbjc4n.r-1habvwh.r-18u37iz.r-1w6e6rj.r-1wtj0ep > div.css-1dbjc4n.r-1adg3ll.r-16l9doz.r-6gpygo.r-2o1y69.r-1v6e3re.r-bztko3.r-1xce0ei > div.r-1p0dtai.r-1pi2tsx.r-1d2f490.r-u8s1d.r-ipm5af.r-13qz1uu > div > div.r-1p0dtai.r-1pi2tsx.r-1d2f490.r-u8s1d.r-ipm5af.r-13qz1uu > div > a > div.css-1dbjc4n.r-14lw9ot.r-sdzlij.r-1wyvozj.r-1udh08x.r-633pao.r-u8s1d.r-1v2oles.r-desppf > div > div.r-1p0dtai.r-1pi2tsx.r-1d2f490.r-u8s1d.r-ipm5af.r-13qz1uu > div > img')
                    profile_img = profile_img.get_attribute('src')
                except:
                    url = None

                try:
                    joined_date = driver.find_element(By.CSS_SELECTOR , '#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div > div > div:nth-child(3) > div > div > div > div.css-1dbjc4n.r-1ifxtd0.r-ymttw5.r-ttdzmv > div:nth-child(4) > div > span.css-901oao.css-16my406.r-14j79pv.r-4qtqp9.r-poiln3.r-1b7u577.r-bcqeeo.r-qvutc0 > span')
                    joined_date = joined_date.text
                except:
                    joined_date = None

                try:
                    profile_data = {
                        'sns' : 'twitter',
                        'name': name,
                        'screen_name': screen_name,
                        'bio': bio,
                        'location': location,
                        'profile_img': profile_img,
                        'joined_date': joined_date
                    }
                    return profile_data
                except:
                    return None
            except:
                return None

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

        # def scrape_instagram_profile(self):
        #     url = f"https://www.instagram.com/{self.username}/"
        #     response = requests.get(url)

        #     if response.ok:
        #         html = response.text
        #         soup = BeautifulSoup(html, 'html.parser')
        #         profile_data = {}
        #         profile_data['sns'] = 'instagram'
        #         profile_data['name'] = soup.select_one('head > title').get_text()
        #         profile_data['description'] = soup.find('meta', {'name': 'description'})['content']

        #         return profile_data
        #     else:
        #         return None



    

    
    
    driver_path = 'app/chromedriver.exe'

    find_name = request.cookies.get("NAME")
    # insta_id = request.cookies.get("insta_id")
    # insta_pw = request.cookies.get("insta_pw")
    # face_id = request.cookies.get("face_id")
    # face_pw = request.cookies.get("face_pw")



    

    # find_name = request.form["NAME"]
    scraper = SNSProfileScraper(find_name , driver_path)
    twitter_profile = scraper.scrape_twitter_profile()
    facebook_profile = scraper.scrape_facebook_profile(Facebook_ID,Facebook_PW)
    instagram_profile = scraper.scrape_instagram_profile(Instagram_ID,Instagram_PW)

    result ={}

    result['twitter'] = twitter_profile
    result['facebook'] = facebook_profile
    result['instagram'] = instagram_profile

    return render_template("sns_result.html", result=result)