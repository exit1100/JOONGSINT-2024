from flask import Flask, session, render_template, redirect, request, url_for, Blueprint
import pymysql
import os
from config import host,port,user,password,db
from module.db_module import init


register_module = Blueprint("register_module", __name__)

@register_module.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@register_module.route("/register", methods=['GET', 'POST'])
def register_result():
    if request.method == 'POST':
        input_db = init(host,port,user,password,db)

        id = request.form['id']
        pw = request.form['pw']

        cursor = input_db.cursor()

        cursor.execute("SELECT * FROM user WHERE id = %s", (id,))
        data = cursor.fetchone()

        if data is None:
            cursor.execute("INSERT INTO user (id, pw) VALUES (%s, %s)", (id, pw))
            cursor.execute("INSERT INTO user_detail (keyword, search_ID, search_domain, search_word, user_id) VALUES ('none','none','none','none', %s)", (id))
            input_db.commit()
            input_db.close()
            return render_template("register_success.html")
        else:
            return render_template("register_fail.html")
        
    return render_template("register.html")
