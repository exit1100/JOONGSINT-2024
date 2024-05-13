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

    cursor.execute("INSERT INTO result (module, type, result, user) VALUES (%s, %s, %s, %s)", (moduel, type, json_result, user))

    db.commit()
    #db.close()


def user_update(db,field,value,user):
    cursor = db.cursor()

    query = "UPDATE user_detail SET {} = %s WHERE user_id = %s".format(field)
    cursor.execute(query, (value, user))

    db.commit()
    #db.close()


def get_setting(db,field,user):
    cursor = db.cursor()

    # query = "SELECT %s FROM user_detail WHERE user_id = %s"
    # cursor.execute(query, (field, user))

    cursor.execute("select " + field + " from user_detail WHERE user_id = %s", (user,))
    
    data = cursor.fetchone()

    db.commit()
    #db.close()

    return data[0]

# config set

# host = '127.0.0.1'
# port = 3306
# user = 'root'
# password = ''
# db = 'joongsint'


