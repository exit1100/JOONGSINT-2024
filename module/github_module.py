from flask import Blueprint, render_template, request, session
import requests, base64, time, re, os, json
from datetime import datetime
from config import github_access_token, host, port, user, password, db
from module.db_module import init, insert, get_setting
from module.login_module import login_required

github_module = Blueprint("github_module", __name__)

@github_module.route("/github_result", methods=["POST"])
@login_required
def github_result():
    class GithubAnalyzer:
        def __init__(self, access_token, username, keywords):
            self.access_token = access_token
            self.username = username
            self.headers = {
                "Authorization": f"Bearer {self.access_token}",
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/vnd.github.v3+json"
            }
            self.keywords = keywords
            self.van_list = ["integrity", "sha512"]
            self.repo_list = []
            self.result_folder = os.path.join(os.getcwd(), self.username)
            self.ip_regex = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            self.phone_regex = r'\b(?:\d{2,3}-)?\d{3,4}-\d{4}\b'
            self.email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
            self.start_time = datetime.today().strftime("%Y%m%d%H%M%S")
            self.log_path = ''
            self.pdf_link = []

            if request.cookies.get('folder') is not None and request.cookies.get('folder') != '':
                self.log_path = './crawling_log/' + request.cookies.get('folder').encode('latin-1').decode('utf-8') + '/github_module'
            else:
                self.log_path = './crawling_log/none/github_module'

            if not os.path.exists(self.log_path):
                os.makedirs(self.log_path)

        def get_user_repositories(self):
            try:
                url = f"https://api.github.com/users/{self.username}/repos"
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    return response.json()
                else:
                    print("Error in get_user_repositories:", response.status_code)
                    return None
            except Exception as e:
                print(f"Exception in get_user_repositories: {e}")
                return None

        def search_repository_contents(self, repository_name, path=""):
            try:
                url = f"https://api.github.com/repos/{self.username}/{repository_name}/contents/{path}"
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    return response.json()
                else:
                    print("Error in search_repository_contents:", response.status_code)
                    return None
            except Exception as e:
                print(f"Exception in search_repository_contents: {e}")
                return None

        def search_file_contents(self, repository_name, file_path):
            try:
                url = f"https://api.github.com/repos/{self.username}/{repository_name}/contents/{file_path}"
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    content = response.json()
                    if "content" in content:
                        return {"content": content["content"], "file_path": file_path}
                    else:
                        print("File content not found.")
                        return None
                else:
                    print("Error in search_file_contents:", response.status_code)
                    return None
            except Exception as e:
                print(f"Exception in search_file_contents: {e}")
                return None

        def traverse_directory(self, repository_name, path=""):
            contents = self.search_repository_contents(repository_name, path)
            if contents is not None:
                for content in contents:
                    if content["type"] == "file":
                        file_path = content["path"]
                        file_result = self.search_file_contents(repository_name, file_path)

                        if file_result is not None:
                            try:
                                file_contents = file_result["content"]
                                file_path = file_result["file_path"]
                                if file_path.endswith(".pdf"):
                                    pdf_url = f"https://github.com/{self.username}/{repository_name}/blob/master/{file_path}?raw=true"
                                    self.pdf_link.append(pdf_url)
                                else:
                                    decoded_content = base64.b64decode(file_contents).decode("utf-8", errors='ignore')
                                    lines = decoded_content.splitlines()
                                    for line in lines:
                                        dicts = {}
                                        if self.keywords:
                                            if not any(van in line for van in self.van_list):
                                                for keyword in self.keywords:
                                                    if re.search(keyword, line, re.IGNORECASE):
                                                        dicts['path'] = file_path
                                                        dicts['content'] = line
                                                        self.repo_list.append(dicts)
                                                        break
                                        else:
                                            if re.search(self.ip_regex, line) or re.search(self.phone_regex, line) or re.search(self.email_regex, line):
                                                dicts['path'] = file_path
                                                dicts['content'] = line
                                                self.repo_list.append(dicts)
                            except UnicodeDecodeError:
                                continue
                    elif content["type"] == "dir":
                        dir_path = content["path"]
                        self.traverse_directory(repository_name, dir_path)
                return self.repo_list
            else:
                return []

        def analyze(self):
            repositories = self.get_user_repositories()
            result = {}
            if repositories is not None:
                sorted_repositories = sorted(repositories, key=lambda x: x.get("stargazers_count", 0), reverse=True)
                for repo in sorted_repositories:
                    repo_name = repo.get("name")
                    if repo_name:
                        self.repo_list = []
                        repo_result = self.traverse_directory(repo_name)
                        if repo_result:
                            result[repo_name] = repo_result
                        time.sleep(1)
                result = {k: v for k, v in result.items() if v}
            else:
                print("No repositories found or error occurred in get_user_repositories.")
            return result, self.pdf_link

    input_db = init(host, port, user, password, db)
    input_user = session['login_user']

    github_username = get_setting(input_db, 'search_ID', input_user)
    filter_keyword = get_setting(input_db, 'keyword', input_user)

    if not github_username or github_username == 'None':
        return "Error: GitHub username not found in database.", 400

    keyword = [k.strip() for k in filter_keyword.split(",")] if filter_keyword and filter_keyword != 'None' else []
    analyzer = GithubAnalyzer(github_access_token, github_username, keyword)

    try:
        result_data, pdf_links = analyzer.analyze()
    except Exception as e:
        print('Error during analysis:', e)
        return f"Error during analysis: {e}", 500

    # PDF 링크를 result_data에 추가
    result_data_with_pdf = {
        "github": result_data,
        "pdf_link": pdf_links
    }

    module = "github"
    type = "enterprise"
    json_result = json.dumps(result_data_with_pdf)
    insert(input_db, module, type, json_result, input_user)
    input_db.close()

    return render_template("github_result.html", filter_keyword=filter_keyword, folder_path=analyzer.log_path, result=result_data_with_pdf)
