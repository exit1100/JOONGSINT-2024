from flask import Flask, session, render_template, redirect, request, url_for, Blueprint
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
