from flask import Blueprint, render_template, request
from datetime import datetime
import os, ast

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


    return render_template("report_result.html", log_path=report.log_path, report_select=report.report_select, domain=domain, network=network, github=github, who=whos)