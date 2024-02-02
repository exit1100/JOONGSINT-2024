from flask import Blueprint, render_template, request
from bs4 import BeautifulSoup
import time, re, os
from urllib.parse import urljoin
from urllib.parse import unquote
from datetime import datetime
import os
import ast

reportlist_module = Blueprint("reportlist_module", __name__)

@reportlist_module.route("/reportlist_result", methods=["POST"])

def reportlist_result():
    start_time = datetime.today().strftime("%Y%m%d%H%M%S")  
    log_path = './crawling_log'
    
    # for filename in os.listdir(directory):
    #             file_path = os.path.join(directory, filename)
    combo = os.listdir(f'{log_path}/')
    result = combo
    return render_template("reportlist_result.html", result=result)

