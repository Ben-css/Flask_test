from flask import *
import pymongo
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField, DateTimeField,
RadioField, SelectField,
TextAreaField,SubmitField)
from wtforms.validators import DataRequired 



client = pymongo.MongoClient("mongodb+srv://root:root123@cluster0.9cjg4lw.mongodb.net/?retryWrites=true&w=majority")
db = client.test

class MyForm(FlaskForm):
    dorm = RadioField('棟別', choices=[('B1','B1'),('B2','B2'),('H','H'),('M','M'),('N','N')])
    place = RadioField('地點',choices=[('寢室','寢室'),('公共區域','公共區域')])
    fixsubject_1 = RadioField('類別', choices=[('電燈','電燈'),('門栓','門栓'),('窗戶','窗戶'),('鏡子','鏡子'),('水龍頭','水龍頭'),('洗衣機','洗衣機'),('烘衣機','烘衣機'),('消防設備','消防設備'),('其他','其他')])
    fixsubject_2 = TextAreaField('其他維修項目')
    explain= TextAreaField('說明')
    submit = SubmitField("確認")


app = Flask(
    __name__,
    static_folder= "static",
    static_url_path= "/"
)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.secret_key = "Hello World"



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signuppage")
def signuppage():
    return render_template("signup.html")
    
@app.route("/signup", methods=["POST"])
def signup():
    account = request.form['account']
    password = request.form['password']
    email =request.form['email']
    name = request.form['name']
    number = request.form['number']

    collection = db.users
    result = collection.find_one({
        "account": account
    })
    if result != None:
        return redirect("/error?msg=信箱已被註冊")
    
    collection.insert_one({
        "account": account,
        "password": password,
        "email": email,
        "name": name,
        "number": number
    })
    return redirect("/")

@app.route("/signin", methods=["POST"])
def signin():
    account = request.form["account"]
    password = request.form["password"]
    # 和資料庫做互動
    collection = db.users
    #檢查帳號密碼是否正確
    result = collection.find_one({
        "$and":[
        {"account": account},
        {"password": password}
        ]
    })
    #登入失敗，到錯誤頁面
    if result == None:
        return redirect("/error?msg=帳號或密碼輸入錯誤")
    # 登入成功，在 session 紀錄會員資訊，到會員頁面
    session["account"] = result["account"]
    print(session['account'])
    return redirect("/member")

@app.route("/member")
def member(): 
    form = MyForm()
    if "account" in session:
        return render_template("member.html",form=form)
    else:
        return redirect("/")
    
@app.route("/error")
def error(): 
    message= request.args.get("msg","發生錯誤")
    return render_template("error.html", message= message)

@app.route("/signout")
def signout():
    del session['account']
    return redirect("/")

app.run(port = 3000, debug=True)

