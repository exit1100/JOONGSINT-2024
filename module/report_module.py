from flask import Blueprint, render_template, request, session
from datetime import datetime
from config import host,port,user,password,db
from module.db_module import init, get_only_result
import json
from module.login_module import login_required 

report_module = Blueprint("report_module", __name__)

@report_module.route("/report_result", methods=["POST"])
@login_required
def report_result():

    input_db = init(host,port,user,password,db)
    input_user = 	session['login_user']
    
    selected_value = request.form.get('report_select')
    tuple_value = eval(selected_value)


    # 튜플의 각 요소를 변수로 저장
    module, date_time = tuple_value

    result = get_only_result(input_db,input_user,module, date_time)
    
    # change json
    json_result = json.loads(result)



    if module == 'facebook':
        json_result['facebook']=json_result
        return render_template("facebook_result.html", result=json_result)
    elif module == 'twitter':
        return render_template("twitter_result.html", result=json_result)
    elif module == 'instagram':
        json_result['instagram']=json_result
        return render_template("insta_result.html", result=json_result)
    elif module == 'domain':
        return render_template("domain_result.html", result=json_result)
    elif module == 'github':
        result_data = json_result
        pdf_links = result_data.get('pdf_link', [])
        return render_template("github_result.html", result=result_data, pdf_link=pdf_links)
    elif module == 'network':
        return render_template("twitter_result.html", result=json_result)
    elif module == 'search':
        result_data = {}
        result_data['onebon'] = json_result.get('onebon', [])
        result_data['result'] = json_result.get('result', [])
        print(result_data)
        return render_template("search_result.html", result=result_data)
    else:
        return render_template('reportlist_result.html')
