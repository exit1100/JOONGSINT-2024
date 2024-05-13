from flask import Flask, render_template , session
from datetime import timedelta

# from module.my_calc_module import my_calc_module
# from module.sns_module import sns_module
# from module.insta_module import insta_module
from module.facebook_module import facebook_module
from module.twitter_module import twitter_module
from module.search_module import search_module
from module.domain_module import domain_module
from module.network_module import network_module
from module.github_module import github_module
from module.report_module import report_module
from module.reportlist_module import reportlist_module
# from module.reportPDF_module import reportPDF_module
from module.login_module import login_module
from module.register_module import register_module
from module.user_setting_module import user_setting_module
# import config as config

app = Flask(__name__)
# app.register_blueprint(my_calc_module)
# app.register_blueprint(sns_module)
# app.register_blueprint(insta_module)
app.register_blueprint(facebook_module)
app.register_blueprint(twitter_module)
app.register_blueprint(search_module)
app.register_blueprint(domain_module)
app.register_blueprint(network_module)
app.register_blueprint(github_module)
app.register_blueprint(report_module)
app.register_blueprint(reportlist_module)
# app.register_blueprint(reportPDF_module)
app.register_blueprint(login_module)
app.register_blueprint(register_module)
app.register_blueprint(user_setting_module)

app.config.from_object('config')

app.secret_key="asdasd"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)

@app.route("/")
def index():
    try:
        return render_template("index.html", user_id=session['login_user'])
    except:
        return render_template("index.html")

@app.route("/hello")
def hello_flask():
    return render_template('loading.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/cveVuln")
def cve_flask():
    return render_template('cveVideo.html')

if __name__ == "__main__":              
    app.run(host="0.0.0.0", port="5000" ,debug=True)
