
from flask import Blueprint, render_template, request, session
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from config import Twitter_ID, Twitter_PW, host, port, user, password, db
from module.db_module import init, insert, get_setting
from module.login_module import login_required

twitter_module = Blueprint("twitter_module", __name__)

@twitter_module.route("/twitter_result", methods=["POST"])
@login_required
def twitter_result():
    class SNSProfileScraper:
        service = Service(executable_path=r'/home/ubuntu/JOONGSINT-2024/app/chromedriver')
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--lang=ko_KR.UTF-8')
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(service=service, options=options)
        
        def __init__(self, username):            
            self.username = username
            self.valError = False
        
        def close_driver(self):
            self.driver.close()
            
        def chk_username(self):
            if self.username == None:
                self.valError = True
            # username이 None이면 에러
            else:
                self.username = str(self.username).replace(' ', '').replace('\t', '').replace('\n', '')
                if (self.username == '') or (self.username == 'none'):
                    self.valError = True
            # username이 공백이면 에러
            
        def login_twitter(self, login_name, login_pw):
            self.driver.get('https://x.com/i/flow/login')
            print('트위터 로그인 페이지 접속')
            element = WebDriverWait(self.driver, 120).until(
                EC.visibility_of_element_located((By.NAME, 'text'))
            )
            self.driver.find_element(By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input').send_keys(login_name)
            # ID 또는 이메일 주소 입력
            self.driver.find_element(By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]/div').click()
            # 확인 버튼 클릭
            print('트위터 이메일 주소 입력')
            try:
                message = self.driver.find_element(By.XPATH, '//*[@id="modal-header"]/span/span').text
                if message == '휴대폰 번호 또는 사용자 아이디 입력':
                # 비정상적인 로그인 다수 시도 예외 처리
                    self.driver.find_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input').send_keys(login_name)
                    # ID 또는 전화번호 입력
                    self.driver.find_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div').click()
                    # 확인 버튼 클릭
            except:
                pass
            element = WebDriverWait(self.driver, 120).until(
                EC.visibility_of_element_located((By.NAME, 'password'))
            )
            self.driver.find_element(By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input').send_keys(login_pw)
            # 패스워드 입력
            self.driver.find_element(By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/button/div').click()
            # 확인 버튼 클릭
            print('트위터 패스워드 입력')
            self.driver.implicitly_wait(3)
            
        def scrape_twitter_profile(self):
            self.chk_username()
            if self.valError == True:
                profile_data = {
                    'sns' : 'twitter',
                    'name': '아이디가 올바르지 않습니다.',
                    'screen_name': '',
                    'bio':  '',
                    'location': '',
                    'profile_img': '',
                    'joined_date': ''
                }
                return profile_data
            
            print('트위터 대상 페이지 접속')
            self.driver.get('https://x.com/'+self.username)
            self.driver.implicitly_wait(3)
        
            # [*] 트위터 프로필 구조
            #   // 프로필 이미지 (고정)
            #   // 아이디 (고정)
            #   // 닉네임 (고정)
            #   // SUMMARY (유동)
            #   // 웹 사이트 주소 (유동)
            #   // 위치 (유동)
            #   // 생년월일 (유동)
            #   // 최초 가입일 (고정)
            
            #try:
            profile_img = self.driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[1]/div[1]/div[2]/div/div[2]/div/a/div[3]/div/div[2]/div/img').get_property('src')
            name = self.driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[2]/div[1]/div/div[1]/div/div/span/span[1]').text
            id = self.driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[2]/div[1]/div/div[2]/div/div/div/span').text
            # except:
            #     profile_data = {
            #         'sns' : 'twitter',
            #         'name': '아이디가 올바르지 않습니다.',
            #         'screen_name': '',
            #         'bio':  '',
            #         'location': '',
            #         'profile_img': '',
            #         'joined_date': ''
            #     }
            #     return profile_data
            
            summary= ''
            location = ''
            joined_date = ''
            propertyCou = 1
            
            try:
                summary = self.driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[3]/div/div/span').text
                locTestId = '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[4]/div/span['+str(propertyCou)+']'
            except:
                locTestId = '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[3]/div/span['+str(propertyCou)+']'
                # summary가 없으면 xPath 상 div 위치가 1 작아짐.
                pass
            
            while(True):
                try:
                    propertyTestId = self.driver.find_element(By.XPATH, locTestId).get_attribute('data-testid')
                    if propertyTestId == 'UserLocation': # 위치 정보
                        location = self.driver.find_element(By.XPATH, locTestId+'/span/span').text
                    elif propertyTestId == 'UserJoinDate': # 최초 가입일 정보
                        joined_date = self.driver.find_element(By.XPATH, locTestId+'/span').text
                    elif (propertyTestId == '') or (propertyTestId == None):
                        break
                    propertyCou += 1
                    locTestId = locTestId.replace('span['+str(propertyCou-1)+']','span['+str(propertyCou)+']')
                    # 다음 순회를 위한 xPath 수정
                except:
                    break

            profile_data = {
                'sns' : 'twitter',
                'name': id,
                'screen_name': name,
                'bio': summary,
                'location': location,
                'profile_img': profile_img,
                'joined_date': joined_date
            }
            return profile_data

    # find_name = request.cookies.get("NAME")
    # 쿠키 방식에서 DB 방식으로 전환함에 따라 주석 처리
    input_db = init(host,port,user,password,db)
    input_user = session['login_user']
    find_name = get_setting(input_db,'search_ID',input_user)
    input_db.close()
    print(find_name)
    
    scraper = SNSProfileScraper(find_name)
    print('driver load.')
    scraper.login_twitter(Twitter_ID, Twitter_PW)
    print('twitter login.')
    twitter_profile = scraper.scrape_twitter_profile()
    print('twitter scraper.')
    scraper.close_driver()
    result ={}
    result['twitter'] = twitter_profile

    module = "twitter"
    type = "enterprice"
    json_result = json.dumps(result['twitter'])
    print("json_result: ", json_result)
    input_db = init(host,port,user,password,db)
    insert(input_db, module, type, json_result, input_user)
    input_db.close()
    
    return render_template("twitter_result.html", result=result)