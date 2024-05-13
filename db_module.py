import pymysql
import os

def init(host,port,user,password,db):
    mysql_host = os.environ.get('MYSQL_HOST', host)
    mysql_port= int(os.environ.get('MYSQL_PORT', port))
    mysql_user =  os.environ.get('MYSQL_USER', user)
    mysql_password = os.environ.get('MYSQL_PASSWORD', password)
    mysql_db = os.environ.get('MYSQL_DB', db)

    db = pymysql.connect(host=mysql_host,port=mysql_port, user=mysql_user, password=mysql_password, db=mysql_db, charset='utf8')

    return db


def insert(db, moduel, type, json_result, user):

    cursor = db.cursor()

    cursor.execute("INSERT INTO result (moduel, type, result, user) VALUES (%s, %s, %s, %s)", (moduel, type, json_result, user))

    db.commit()
    db.close()