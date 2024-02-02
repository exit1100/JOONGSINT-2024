from flask import Blueprint, render_template, request
import requests, base64, time, re, os
from config import github_access_token
from datetime import datetime

github_module = Blueprint("github_module", __name__)

@github_module.route("/github_result", methods=["POST"])
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
            
            if request.cookies.get('folder') is not None and request.cookies.get('folder') != '' :
                self.log_path = './crawling_log/' + request.cookies.get('folder').encode('latin-1').decode('utf-8') + '/github_module'
            else:
                self.log_path = './crawling_log/none/github_module'

            if not os.path.exists(self.log_path):
                os.makedirs(self.log_path)
                
        def get_user_repositories(self):
            url = f"https://api.github.com/users/{self.username}/repos"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                repositories = response.json()
                return repositories
            else:
                print("Error:", response.status_code)
                print("Response:", response.text)
                return None

        def search_repository_contents(self, repository_name, path=""):
            url = f"https://api.github.com/repos/{self.username}/{repository_name}/contents/{path}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                contents = response.json()
                return contents
            else:
                print("Error:", response.status_code)
                print("Response:", response.text)
                return None

        def search_file_contents(self, repository_name, file_path):
            url = f"https://api.github.com/repos/{self.username}/{repository_name}/contents/{file_path}"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                content = response.json()
                if "content" in content:
                    return {"content": content["content"], "file_path": file_path}
                else:
                    print("File content not found.")
            else:
                print("Error2:", response.status_code)
                print("Response:", response.text)

        def traverse_directory(self, repository_name, path=""):
            contents = self.search_repository_contents(repository_name, path)
            
            if contents is not None:
                for content in contents:
                    if content["type"] == "file":
                        file_path =  content["path"]
                        file_result = self.search_file_contents(repository_name, file_path)

                        if file_result is not None:
                            try:
                                file_contents = file_result["content"]
                                file_path = file_result["file_path"]
                                # Check if the file is a PDF
                                if file_path.endswith(".pdf"):
                                    # Get the download URL of the PDF
                                    pdf_url = f"https://github.com/{self.username}/{repository_name}/blob/master/{file_path}?raw=true"
                                    # Save the download URL into the file 'pdf_link.txt'
                                    self.pdf_link.append(pdf_url)
                                else:
                                    decoded_content = base64.b64decode(file_contents).decode("utf-8")
                                    lines = decoded_content.splitlines()
                                    for line in lines:
                                        dicts = {}
                                        for keyword in self.keywords:
                                            if re.search(keyword, line, re.IGNORECASE) and not any(van in line for van in self.van_list):
                                                dicts['path'] = file_path
                                                dicts['content'] = line
                                                self.repo_list.append(dicts)
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

        def analyze(self):
            repositories = self.get_user_repositories()
            result = {}
            if repositories is not None:
                sorted_repositories = sorted(repositories, key=lambda x: x["stargazers_count"], reverse=True)
                
                repository_names = []
                
                for repo in sorted_repositories:
                    repository_names.append(repo["name"])
                    print(repo["name"])


                for repo_name in repository_names:
                    self.repo_list = []
                    repo_result = self.traverse_directory(repo_name)
                    result[repo_name] = repo_result
                    time.sleep(1)
            del_list = []

            for i in range(len(result)):
                if len(list(result.values())[i]) == 0:
                    del_list.append(list(result.keys())[i])
                else:
                    pass
            for i in range(len(del_list)):
                del result[del_list[i]]
            fp = open(f'{self.log_path}/{self.start_time}.txt','w', encoding='utf-8')
            fp.write(self.username+"$"+str(result))
            fp.close()
            
            return result,self.pdf_link

    github_username = request.cookies.get('NAME')
    print(github_username)
    filter_keyword = ''
    if request.cookies.get('keyword') not in [None, ''] :
        filter_keyword = request.cookies.get('keyword').encode('latin-1').decode('utf-8')
        keyword = [filter_keyword.strip() for filter_keyword in filter_keyword.split(",")]
    else :
        filter_keyword = 'no_keyword'
        keyword = []
    analyzer = GithubAnalyzer(github_access_token, github_username, keyword)
    try:
        result,pdf_links = analyzer.analyze()
    except:
        print('error')
        pass
    result_key = list(result.keys())


    return render_template("github_result.html", filter_keyword=filter_keyword, folder_path=analyzer.log_path, result=result, result_key=result_key,pdf_link = pdf_links)