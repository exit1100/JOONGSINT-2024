from flask import Blueprint, render_template, request, session
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time, re, os, json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config import host, port, user, password, db
from module.db_module import init, insert, get_setting
from module.login_module import login_required 

domain_module = Blueprint("domain_module", __name__)

@domain_module.route("/domain_result", methods=["GET", "POST"])
@login_required
def domain_result():
    class WebCrawler:
        def __init__(self, filter_key=None, options=None):
            #options=Options()
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--lang=ko_KR.UTF-8')
            self.driver = webdriver.Chrome(executable_path=r'app/chromedriver', options=options)
            
            #service = Service(executable_path=r'app/chromedriver')
            #self.driver=webdriver.Chrome(service=service,options=options)

            self.category = ['keywords', 'emails', 'phones']
            self.all_url = []
            self.complete_url = []
            self.search_url = []
            self.result = {}
            self.all_keyword = []
            self.all_email = []
            self.all_phone = []
            self.keyword_str = 'none'
            self.filter_flag = False
            self.capute_path = './capture_page'

            if filter_key is not None and filter_key != '' :
                self.filter_flag = True
                self.keyword_str = filter_key
                self.keyword_list = [value.strip() for value in self.keyword_str.split(',')]

        def HTML_SRC(self, url, url_search=0, filter=False):
            try:
                self.driver.get(url)

                while True: # hold
                    page_state = self.driver.execute_script('return document.readyState;')
                    if page_state == 'complete':
                        break
                    time.sleep(1)

                # SPA WebPage HTML Crawling
                html = self.driver.execute_script('return document.getElementsByTagName("html")[0].innerHTML;')

                # BeautifulSoup html 추출
                soup = BeautifulSoup(html, 'html.parser')
                if (url_search==1):
                    return soup
                
                if (filter==True):
                    filter_flag = False
                    for target_string in self.keyword_list:
                        if target_string in soup.text:
                            filter_flag = True
                            break
                    if (filter_flag == False):
                        return

                self.search_url.append(url)
                keywords = re.findall(r"[가-힣]{2,10}", soup.text)
                for keyword in keywords:
                    if keyword not in self.all_keyword:
                        self.all_keyword.append(keyword)

                emails = re.findall(r'\b[\w.-]+?@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,63}\b', soup.text)
                for email in emails:
                    if email not in self.all_email:
                        self.all_email.append(email)

                phones = re.findall(r"\d{2,3}-\d{3,4}-\d{4}", soup.text)
                for phone in phones:
                    if phone not in self.all_phone:
                        self.all_phone.append(phone)

                value = []
                tmp = {}
                for key in self.category:
                    tmp[key] = locals()[key]
                tmp['filter_keyword'] = self.keyword_str
                value.append(tmp)

                # URL Capture
                #invalid_chars = r'[\\/:\*\?"<>\|]+' # 파일 이름으로 사용할 수 없는 문자들을 '_'로 치환
                #filename = re.sub(invalid_chars, '_', url) + '.png'
                #self.driver.set_window_size(1920, 1080)
                #wait = WebDriverWait(self.driver, 10) # 페이지 로딩이 완료될 때까지 대기
                #wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
                #self.driver.save_screenshot(f'{self.capute_path}/{filename}')
            except:
                pass

        def url_append(self, url, depth=1):
            try:
                if (depth < 1) : return
                depth -= 1
                self.complete_url.append(url)
                
                soup = self.HTML_SRC(url, 1)
                for link in soup.find_all("a"):
                    url_add = urljoin(url, link.get("href"))
                    if url_add not in self.all_url:
                        self.all_url.append(url_add) 
                for url_one in (set(self.all_url) - set(self.complete_url)):
                    self.url_append(url_one, depth)     
            except:
                return

        def run(self, root_url):
            self.url_append(root_url, 1)
            print('keyword :',self.keyword_str)
            #if not os.path.exists(self.capute_path):
            #    os.makedirs(self.capute_path)

            for url in self.all_url:
                print("[*] Target URL:" ,url, '###')
                if (self.filter_flag) :
                    self.HTML_SRC(url, 0, True)   
                else :
                    self.HTML_SRC(url)

            self.result['keyword'] = self.all_keyword
            self.result['email'] = self.all_email
            self.result['phone'] = self.all_phone
            self.result['search_url'] = self.search_url
            return self.result

    # db init
    input_db = init(host,port,user,password,db)
    moduel = "domain"
    type = "enterprice"
    input_user = session['login_user']

    domain = get_setting(input_db,'search_domain',input_user)

    filter_key = get_setting(input_db,'keyword',input_user)

    # start domain module
    url = 'http://'+ domain +'/'
    #print(url)
    
    crawling = WebCrawler(filter_key)
    result = crawling.run(url)
    #print(result)
    json_result = json.dumps(result)

    # db insert
    insert(input_db, moduel, type, json_result, input_user)
    input_db.close()

    return render_template("domain_result.html", filter_keyword=crawling.keyword_str, result=result)
