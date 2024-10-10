from flask import Blueprint, render_template, request, session
import re
import requests
import urllib.parse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import google_api_key, google_cse_id, naver_client_id, naver_client_secret
from config import host, port, user, password, db
from module.db_module import init, insert, get_setting
import json
from module.login_module import login_required 

search_module = Blueprint("search_module", __name__)

@search_module.route("/search_result", methods=["POST"])
@login_required
def search_result():
    class SearchAgent:
        def __init__(self, google_api_key, google_cse_id, naver_client_id, naver_client_secret):
            self.google_api_key = google_api_key
            self.google_cse_id = google_cse_id
            self.naver_client_id = naver_client_id
            self.naver_client_secret = naver_client_secret
            self.search_results_one = []
            self.search_results = []
            self.banlist = ['twitter', '.pdf', 'wikipedia', 'youtube']
            
        def google_search(self, search_term, page):
            start_index = (page - 1) * 10 + 1
            try:
                service = build("customsearch", "v1", developerKey=self.google_api_key)
                res = service.cse().list(q=search_term, cx=self.google_cse_id, start=start_index).execute()
                urls_titles = [(item["link"], item["title"]) for item in res["items"]]
                self.search_results_one = urls_titles

                for url, title in urls_titles:
                    if any(banned in url for banned in self.banlist):
                        continue
                    try:
                        res = requests.get(url)
                        html = res.text
                        email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                        phone_regex = r"\d{3}-\d{3,4}-\d{4}"
                        email = re.search(email_regex, html).group() if re.search(email_regex, html) else None
                        phone = re.search(phone_regex, html).group() if re.search(phone_regex, html) else None
                        if email or phone:
                            self.search_results.append([title, url, [phone, email]])
                    except:
                        pass
            except HttpError as error:
                print("An error occurred: %s" % error)

        def naver_search(self, search_term, page):
            start_index = (page - 1) * 10 + 1
            query = urllib.parse.quote(search_term)
            url = f"https://openapi.naver.com/v1/search/webkr?query={query}&display=10&start={start_index}"
            headers = {"X-Naver-Client-Id": self.naver_client_id, "X-Naver-Client-Secret": self.naver_client_secret}
            res = requests.get(url, headers=headers)
            data = res.json()
            urls = [item["link"] for item in data["items"]]

            for url in urls:
                if any(banned in url for banned in self.banlist):
                    continue
                try:
                    res = requests.get(url)
                    html = res.text
                    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                    phone_regex = r"\d{3}-\d{3,4}-\d{4}"
                    email = re.search(email_regex, html).group() if re.search(email_regex, html) else None
                    phone = re.search(phone_regex, html).group() if re.search(phone_regex, html) else None
                    if email or phone:
                        self.search_results.append([url, [phone, email]])
                except:
                    pass

        def run_search(self, query):
            for page in range(1, 2):
                self.google_search(query, page)
            for page in range(1, 2):
                self.naver_search(query, page)

    # 검색어를 데이터베이스에서 가져오기
    input_db = init(host, port, user, password, db)
    input_user = session['login_user']
    search_term = get_setting(input_db, 'search_word', input_user)
    input_db.close()

    search_agent = SearchAgent(google_api_key, google_cse_id, naver_client_id, naver_client_secret)
    search_agent.run_search(search_term)

    # 결과를 JSON 형식으로 저장 (search_results_one과 search_results 모두 저장)
    combined_results = {
        "onebon": search_agent.search_results_one,
        "result": search_agent.search_results
    }
    json_result = json.dumps(combined_results, ensure_ascii=False)
    module = "search"
    type = "enterprice"
    input_db = init(host, port, user, password, db)
    
    # insert 함수를 호출할 때 combined_results를 전달
    insert(input_db, module, type, json_result, input_user)
    input_db.close()

    # combined_results가 템플릿에 정상적으로 전달되도록 수정
    return render_template("search_result.html", result=combined_results)
