from flask import Blueprint, render_template, request, session
from datetime import datetime
from config import host,port,user,password,db
from module.db_module import init, get_only_result
import json

report_module = Blueprint("report_module", __name__)

@report_module.route("/report_result", methods=["POST"])
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
        return render_template("github_result.html", result=json_result)
    elif module == 'network':
        return render_template("twitter_result.html", result=json_result)
    elif module == 'search':
        return render_template("twitter_result.html", result=json_result)
    else:
        return render_template('reportlist_result.html')
