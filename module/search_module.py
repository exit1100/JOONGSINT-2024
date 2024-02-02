from flask import Blueprint, render_template, request
import re
import requests
import urllib.parse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import openai
from config import google_api_key ,google_cse_id,naver_client_id,naver_client_secret,openai_api_key

search_module = Blueprint("search_module", __name__)

@search_module.route("/search_result", methods=["POST"])
def search_result():
    class SearchAgent:
        def __init__(self, google_api_key, google_cse_id, naver_client_id, naver_client_secret, openai_api_key):
            self.google_api_key = google_api_key
            self.google_cse_id = google_cse_id
            self.naver_client_id = naver_client_id
            self.naver_client_secret = naver_client_secret
            self.openai_api_key = openai_api_key
            self.search_results_one = []
            self.search_results = []
            self.gpt_results = ""
            self.banlist = ['twitter', '.pdf', 'wikipedia', 'youtube']
            openai.api_key = openai_api_key
            self.openai = openai

        def gpt_search(self, search_term):
            question = search_term
            response = self.openai.Completion.create(
                model="text-davinci-003",
                prompt=f"{question}에 대해서 알려줘",
                max_tokens=4000
            )
            answer = response.choices[0].text.strip()
            self.gpt_results = answer
            

        def google_search(self, search_term, page):
            # 검색 시작 인덱스 계산
            start_index = (page - 1) * 10 + 1
        
            # 검색 API를 이용해 검색
            try:
                service = build("customsearch", "v1", developerKey=self.google_api_key)
                res = service.cse().list(q=search_term, cx=self.google_cse_id, start=start_index).execute()

                # 검색 결과에서 URL과 제목 추출
                urls_titles = [(item["link"], item["title"]) for item in res["items"]]

                self.search_results_one=urls_titles

                # 추출한 URL에서 이메일과 전화번호 찾기
                for url, title in urls_titles:
                    if any(banned in url for banned in self.banlist):
                        continue
                    try:
                        # URL에서 HTML 가져오기
                        res = requests.get(url)
                        html = res.text

                        # 이메일 찾기
                        email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                        email_match = re.search(email_regex, html)
                        if email_match:
                            email = email_match.group()
                        else:
                            email = None

                        # 전화번호 찾기
                        phone_regex = r"\d{3}-\d{3,4}-\d{4}"
                        phone_match = re.search(phone_regex, html)
                        if phone_match:
                            phone = phone_match.group()
                        else:
                            phone = None

                        # 이메일이나 전화번호가 있는 경우 결과 리스트에 추가
                        if email or phone:
                            self.search_results.append([title, url, [phone, email]])
                    except:
                        pass
                        

            except HttpError as error:
                print("An error occurred: %s" % error)
        
        def naver_search(self, search_term, page):
            # 검색 시작 인덱스 계산
            start_index = (page - 1) * 10 + 1

            # 검색어 인코딩
            query = urllib.parse.quote(search_term)

            # 네이버 검색 API를 이용해 검색
            url = f"https://openapi.naver.com/v1/search/webkr?query={query}&display=10&start={start_index}"
            headers = {"X-Naver-Client-Id": self.naver_client_id, "X-Naver-Client-Secret": self.naver_client_secret}
            res = requests.get(url, headers=headers)

            # 검색 결과에서 URL 추출
            data = res.json()
            urls = [item["link"] for item in data["items"]]
                # 추출한 URL에서 이메일과 전화번호 찾기
            for url in urls:
                # 이미 검색한 URL인 경우 패스
                if url in [item[0] for item in self.search_results]:
                    continue

            # URL에 금지어가 있는 경우 패스
                if any(banned in url for banned in self.banlist):
                    continue

                try:
                    # URL에서 HTML 가져오기
                    res = requests.get(url)
                    html = res.text

                    # 이메일 찾기
                    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                    email_match = re.search(email_regex, html)
                    if email_match:
                        email = email_match.group()
                    else:
                        email = None

                    # 전화번호 찾기
                    phone_regex = r"\d{3}-\d{3,4}-\d{4}"
                    phone_match = re.search(phone_regex, html)
                    if phone_match:
                        phone = phone_match.group()
                    else:
                        phone = None

                # 이메일이나 전화번호가 있는 경우 결과 리스트에 추가
                    if email or phone:
                        self.search_results.append([res.url, [phone, email]])

                except:
                    pass



        def run_search(self, query):
            # 구글 검색 실행
            for page in range(1, 2):
                self.google_search(query, page)

        # 네이버 검색 실행
            for page in range(1, 2):
                self.naver_search(query, page)
            
            self.gpt_search(query)





    # 클래스의 객체 생성
    print(google_api_key,google_cse_id,naver_client_id,naver_client_secret,openai_api_key)
    search_agent = SearchAgent(google_api_key,google_cse_id,naver_client_id,naver_client_secret,openai_api_key)
    # 검색어 입력 받기
    search_term = request.cookies.get("search").encode('latin1').decode('utf-8')
    # 검색어를 이용한 검색 실행 및 결과 저장
    search_agent.run_search(search_term)


    result ={}

    return render_template("search_result.html", result=search_agent.search_results ,onebon = search_agent.search_results_one , gpt_answer = search_agent.gpt_results)

