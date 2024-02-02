from flask import render_template, Blueprint, request
import re
import subprocess
import socket
import dns.resolver
import whois
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas
import time, os
from datetime import datetime


network_module = Blueprint("network_module", __name__)

@network_module.route('/network_result', methods=["POST"])
def network_result():
    class DomainScanner:

        def __init__(self, target_domain):
            self.target_domain = target_domain
            self.ip = socket.gethostbyname(target_domain)
            self._nmap_result = None
            

        def get_ip_info(self):
            """
            IP 정보 가져오기
            """
            try:
                hostname = socket.gethostbyaddr(self.ip)[0]
                return (f"{self.ip}의 호스트 이름: {hostname}")
            except:
                return (f"{self.ip}의 호스트 이름을 찾을 수 없습니다.")



        def get_whois_info(self):
            """
            Whois 정보 가져오기
            """
            domain = self.target_domain
            whois_result = whois.whois(f"{domain}")
            return {
                "domain_name": whois_result['domain_name'],
                "whois_server":whois_result['whois_server'],
                "creation_date":whois_result['creation_date'],
                "updated_date":whois_result['updated_date'],
                "expiration_date":whois_result['expiration_date'],
                "name_servers":whois_result['name_servers'],
                "status":whois_result['status'],
                "emails":whois_result['emails'],
                "name":whois_result['name'],
                "org":whois_result['org'],
                "address":whois_result['address'],
                "city":whois_result['city'],
                "country":whois_result['country'],

            }



        def run_nmap(self):
            """
            Nmap 실행
            """
            command = f"nmap -sS -Pn -p 1-3000 --script dns-brute.nse {self.target_domain} "
            result = subprocess.check_output(command, shell=True, encoding='cp949')

            # IP 주소 추출
            ip_address = re.search(r'Nmap scan report for .* \((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\)', result).group(1)

            # rDNS 레코드 추출
            rdns_record = re.search(r'rDNS record for .*: (.*)', result).group(1)


            # 포트 정보 추출
            port_info = re.findall(r'\d+\/\w+\s+\w+\s+\w+', result)
            port_numbers = [line.split('/')[0] for line in port_info]

            # DNS 브루트포스 결과의 도메인 및 IP 주소 추출
            dns_brute = re.findall(r'\s+\|\s+(\S+)\s+-\s+([\d:.]+)', result)

            # DNS 브루트포스 결과 |_가 존재하는 마지막 라인 
            dns_brute_last = re.findall(r'\s+\|_\s+(\S+)\s+-\s+([\d:.]+)', result)
            #두 리스트 합치기 
            dns_brute.extend(dns_brute_last)

            return {
                "ip_address": ip_address,
                "rdns_records": rdns_record,
                "port_info": port_info,
                "port_numbers": port_numbers,
                "subdomains": dns_brute,
            }


        def get_server_version(self):
            """
            서버 버전 가져오기
            """
            ports = [int(p) for p in self.run_nmap()["port_numbers"]]
            server_info = []
            for port in ports:
                try:
                    response = requests.get("http://" + self.target_domain + ":" + str(port), timeout=1)  # GET 요청 보내기
                    if response:  # 응답 객체가 None이 아닌 경우에만 처리
                        if response.status_code == 200:  # 응답 코드가 200이면(정상 응답)
                            if 'Server' in response.headers:
                                server_version = response.headers["Server"]  # 서버 버전 정보 가져오기
                                server_info.append(server_version.split('/')[0] + '/' + server_version.split('/')[1].split()[0])

                            else:  # 서버 헤더가 없으면
                                soup = BeautifulSoup(response.text, "html.parser")  # BeautifulSoup 객체 생성
                                server_tag = soup.find("meta", attrs={"name": "generator"})  # <meta name="generator" content="...">
                                if server_tag:
                                    server_version = server_tag.get("content")
                                    server_info.append(server_version.split('/')[0] + '/' + server_version.split('/')[1].split()[0])                 
                except Exception as e:
                    pass

            if server_info:
                return server_info
            else:
                return None

        def get_cve_info(self, server_info):
            server_info = server_info.replace("/", " ")
            base_url = "https://services.nvd.nist.gov/rest/json/cves/1.0"
            cve_data = []

            params = {
                "keyword": server_info,
                "resultsPerPage": 50
            }

            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                for result in data["result"]["CVE_Items"]:
                    cve_id = result["cve"]["CVE_data_meta"]["ID"]
                    description = result["cve"]["description"]["description_data"][0]["value"]
                    cvss_score = result["impact"]["baseMetricV3"]["cvssV3"]["baseScore"]
                    categories = result["cve"]["problemtype"]["problemtype_data"][0]["description"][0]["value"]
                    cve_data.append({"CVE ID": cve_id, "Description": description, "CVSS Score": cvss_score, "Category": categories})
            else:
                print(f"Error: {response.status_code}")

            return cve_data
    # DomainScanner 객체 생성
    domain_scanner = DomainScanner('www.joongsint.com')

    # 네트워크 결과 가져오기
    try:
        ip_info = domain_scanner.get_ip_info()
        print(ip_info)
    except:
        ip_info='ip_info'
        print(ip_info)
    
    try:
        whois_info = domain_scanner.get_whois_info()
    except:
        whois_info='whois_info'
        print(whois_info)
    nmap_result = domain_scanner.run_nmap()
    
    try:
        server_info = domain_scanner.get_server_version()
    except:
        server_info='server_info'
        print(server_info)
    
    cve_info = []
    for i in range(len(server_info)):
        cve_info.append(domain_scanner.get_cve_info(server_info[i]))

    # log file save
    log_path = ''
    if request.cookies.get('folder') is not None and request.cookies.get('folder') != '' :
        log_path = './crawling_log/' + request.cookies.get('folder').encode('latin-1').decode('utf-8') + '/network_module'
    else:
        log_path = './crawling_log/none/network_module'
    start_time = datetime.today().strftime("%Y%m%d%H%M%S")

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    result_dic = {}
    result_dic['ip_info'] = ip_info
    #result_dic['whois_info'] = whois_info
    result_dic['nmap_result'] = nmap_result
    result_dic['server_info'] = server_info
    result_dic['cve_info'] = cve_info

    fp = open(f'{log_path}/{start_time}.txt','w', encoding='utf-8')
    fp.write(str(result_dic))
    fp.close()

    # HTML 파일에 결과 값 전달
    return render_template('network_result.html', ip_info=ip_info, whois_info=whois_info, nmap_result=nmap_result, server_info=server_info, cve_info=cve_info)
