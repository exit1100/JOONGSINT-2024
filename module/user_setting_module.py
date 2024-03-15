from flask import Blueprint, render_template, request, jsonify, session
from module.db_module import init, user_update
from config import host,port,user,password,db

user_setting_module = Blueprint("user_setting_module", __name__)

@user_setting_module.route("/save_data", methods=["POST"])
def save_data():

    saved_values = {"keyword": "", "profileID": ""}  # 필요한 필드 추가
    
    data = request.json
    field = data.get("field")
    value = data.get("value")

    print(field,value)

    input_db = init(host,port,user,password,db)
    input_user = 	session['login_user']
    user_update(input_db,field,value,input_user)

    return jsonify({"success": True})

@user_setting_module.route("/setting", methods=["GET"])
def get_data():
    input_db = init(host, port, user, password, db)
    input_user = session.get('login_user')
    if input_user:

        cursor = input_db.cursor()
        cursor.execute("SELECT keyword ,search_ID, search_domain, search_word, user_id FROM user_detail WHERE user_id = %s", (input_user,))
        data = cursor.fetchone()  # 예시로 한 행만 가져옴
        input_db.close()

        # 가져온 데이터를 JSON 형식으로 반환
        return render_template("setting.html", saved_values=data)


