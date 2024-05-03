from flask import Blueprint, render_template, request
from datetime import datetime
import os, ast
from datetime import datetime
import time
import pymysql
import os
import json

report_module = Blueprint("report_module", __name__)

@report_module.route("/report_result", methods=["POST"])
def report_result():
    class Report:
        def __init__(self):
            self.start_time = datetime.today().strftime("%Y%m%d%H%M%S")  
            self.log_path = ''
            self.report_select = request.form.get('report_select')
            
            if request.cookies.get('folder') is not None and request.cookies.get('folder') != '' :
                self.log_path = './crawling_log/' + self.report_select + '/'
            else:
                self.log_path = './crawling_log/none/'

        def split_name(selt, directory):
            dict_names = []
            who = None
            try:
                for data_path in os.listdir(f'{directory}/'):
                    with open(f'{directory}/{data_path}', 'r',encoding='utf-8') as file:
                        data = file.read()
                        rdata = str(data).split('$')
                        who = rdata[0]
                        rdata = rdata[1]
                        data_list = ast.literal_eval(rdata)
                    dict_names.append(data_list)
            except:
                pass
            return dict_names , who

        def extract_dict_names(self, directory):
            dict_names = []
            try:
                for data_path in os.listdir(f'{directory}/'):
                    with open(f'{directory}/{data_path}', 'r', encoding='utf-8') as file:
                        data = file.read()
                        data_list = ast.literal_eval(data)
                    dict_names.append(data_list)
            except:
                pass
            return dict_names


    
        
    report = Report()
    current_directory = os.getcwd()
    print(f"current path: {report.log_path}")
    domain_path = f'{report.log_path}domain_module' 
    domain = report.extract_dict_names(domain_path)

    network_path = f'{report.log_path}network_module'
    network = report.extract_dict_names(network_path)

    github_path = f'{report.log_path}github_module'
    github, whos = report.split_name(github_path)

    mysql_host = os.environ.get('MYSQL_HOST', '127.0.0.1')
    mysql_port= int(os.environ.get('MYSQL_PORT', 3306))
    mysql_user =  os.environ.get('MYSQL_USER', 'root')
    mysql_password = os.environ.get('MYSQL_PASSWORD', '7575')
    mysql_db = os.environ.get('MYSQL_DB', 'osint')

    result ={}

    db = pymysql.connect(host=mysql_host,port=mysql_port, user=mysql_user, password=mysql_password, db=mysql_db, charset='utf8')

    cursor = db.cursor()
    
    # domain result DB
    sql_domain = "SELECT * FROM result WHERE module = 'domain'"
    cursor.execute(sql_domain)
    results_domain = cursor.fetchall()

    # network result DB
    sql_network = "SELECT * FROM result WHERE module = 'network'"
    cursor.execute(sql_network)
    results_network = cursor.fetchall()

    # git result DB
    sql_git = "SELECT * FROM result WHERE module = 'github'"
    cursor.execute(sql_git)
    results_git = cursor.fetchall()

    # search result DB
    sql_search = "SELECT * FROM result WHERE module = 'search'"
    cursor.execute(sql_search)
    results_search = cursor.fetchall()

    db.commit()
    db.close()

    # domain module
    results_domain_as_dict = []
    for result in results_domain:
        results_domain_as_dict.append({
            'module': result[0],
            'type': result[1],
            'json_result': json.loads(result[2]),
            'user': result[3],
            'date': result[4],
            })
        
    # network module
    results_network_as_dict = []
    for result in results_network:
        results_network_as_dict.append({
            'module': result[0],
            'type': result[1],
            'json_result': json.loads(result[2]),
            'user': result[3],
            'date': result[4],
            })
        
    # git module
    results_git_as_dict = []
    for result in results_git:
        results_git_as_dict.append({
            'module': result[0],
            'type': result[1],
            'json_result': json.loads(result[2]),
            'user': result[3],
            'date': result[4],
            })

    # search module
    results_search_as_dict = []
    for result in results_search:
        results_search_as_dict.append({
            'module': result[0],
            'type': result[1],
            'json_result': json.loads(result[2]),
            'user': result[3],
            'date': result[4],
            })


        

    # 결과를 템플릿에 전달
    return render_template("report_result.html", log_path=report.log_path, report_select=report.report_select, domain=domain, network=network, github=github, who=whos, results_search=results_search_as_dict, results_domain=results_domain_as_dict, results_network=results_network_as_dict, results_git=results_git_as_dict)
