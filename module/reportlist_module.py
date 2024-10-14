from flask import Blueprint, render_template, request, session
from bs4 import BeautifulSoup
import time, re, os
from urllib.parse import urljoin
from urllib.parse import unquote
from datetime import datetime
import os
import ast
from config import host,port,user,password,db
from module.db_module import init, get_result
import datetime
from module.login_module import login_required 

reportlist_module = Blueprint("reportlist_module", __name__)

@reportlist_module.route("/reportlist_result", methods=["POST"])
@login_required
def reportlist_result():

    input_db = init(host,port,user,password,db)
    input_user = 	session['login_user']

    list = get_result(input_db,input_user)

    # 날짜를 기준으로 내림차순 정렬
    sorted_list = sorted(list, key=lambda item: item[1], reverse=True)

    # 데이터 포맷팅 (날짜 형식을 원하는 형태로 변환)
    formatted_data = [(item[0], item[1].strftime('%Y-%m-%d %H:%M:%S')) for item in sorted_list]

    print(formatted_data)
    result = formatted_data

    return render_template("reportlist_result.html", result=result)

