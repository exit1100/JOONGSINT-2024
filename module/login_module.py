from flask import Flask, session, render_template, redirect, request, url_for, Blueprint, g
from functools import wraps
from datetime import timedelta
import pymysql
import os
from config import host,port,user,password,db
from module.db_module import init

login_module = Blueprint("login_module", __name__)

@login_module.route("/login", methods=['GET', 'POST'])
def login_result():
    if request.method == 'POST':
        error = None

        input_db = init(host,port,user,password,db)

        id = request.form['id']
        pw = request.form['pw']

        cursor = input_db.cursor()

        sql = "SELECT id FROM user WHERE id = %s AND pw = %s"
        value = (id, pw)

        cursor.execute(sql, value)

        data = cursor.fetchone()
        input_db.commit()
        input_db.close()

        if data:
            session['login_user'] = data[0]
            # app.permanent_session_lifetime = timedelta(days=1)
            # 세션 유지
            session.permanent = True
            return render_template("index.html", user_id=data[0])
        else:
            error = 'invalid input data detected !'
            return render_template("error.html", error=error)
        
    return render_template("login.html")

@login_module.route("/logout", methods=['GET'])
def logout():
    session.pop('login_user', None)
    return render_template("index.html")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'login_user' not in session:
            # 로그인하지 않은 사용자는 error_page로 리다이렉트
            return redirect(url_for('login_module.error_page'))
        return f(*args, **kwargs)
    return decorated_function

@login_module.route("/error2")
def error_page():
    # error2.html에 필요한 메시지와 버튼의 링크를 전달
    return render_template("error2.html", message="로그인한 사용자만 이용할 수 있는 기능입니다.", login_url=url_for('login_module.login_result'), home_url=url_for('index'))
