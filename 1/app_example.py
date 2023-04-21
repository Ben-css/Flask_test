from flask import *
import pymongo
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField, DateTimeField,
                     RadioField, SelectField,
                     TextAreaField, SubmitField)
from wtforms.validators import DataRequired
import pytz
import json


client = pymongo.MongoClient(
    "mongodb+srv://root:root123@cluster0.9cjg4lw.mongodb.net/?retryWrites=true&w=majority")
db = client.test


class MyForm(FlaskForm):
    dorm = RadioField(
        '棟別', choices=[('B1', 'B1'), ('B2', 'B2'), ('H', 'H'), ('M', 'M'), ('N', 'N')])
    place = RadioField('地點', choices=[('寢室', '寢室'), ('公共區域', '公共區域')])
    fixsubject_1 = RadioField('類別', choices=[('電燈', '電燈'), ('門栓', '門栓'), ('窗戶', '窗戶'), (
        '鏡子', '鏡子'), ('水龍頭', '水龍頭'), ('洗衣機', '洗衣機'), ('烘衣機', '烘衣機'), ('消防設備', '消防設備'), ('其他', '其他')])
    fixsubject_2 = TextAreaField('其他維修項目')
    explain = TextAreaField('說明')
    submit = SubmitField("確認")


app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/"
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
    studentid = request.form['studentid']
    password = request.form['password']
    email = request.form['email']
    name = request.form['name']
    number = request.form['number']

    collection = db.users
    result = collection.find_one({
        "studentid": studentid
    })
    if result != None:
        return redirect("/error?msg=信箱已被註冊")

    collection.insert_one({
        "studentid": studentid,
        "password": password,
        "email": email,
        "name": name,
        "number": number
    })
    return redirect("/")


@app.route("/signin", methods=["POST"])
def signin():
    studentid = request.form["studentid"]
    password = request.form["password"]
    # 和資料庫做互動
    collection = db.users
    # 檢查帳號密碼是否正確
    result = collection.find_one({
        "$and": [
            {"studentid": studentid},
            {"password": password},
        ]
    })

    # 登入失敗，到錯誤頁面
    if result == None:
        return redirect("/error?msg=帳號或密碼輸入錯誤")
    # 登入成功，在 session 紀錄會員資訊，到會員頁面
    session["studentid"] = result["studentid"]
    session["name"] = result["name"]
    print(session['studentid'])
    return redirect("/member")


@app.route("/member")
def member():
    form = MyForm()
    # 如果studentid在session才能登入
    if "studentid" in session:

        return render_template("member.html",
                               form=form,
                               name=session.get('name'),
                               studentid=session.get('studentid'),         
                               )
    else:
        return redirect("/")


@app.route("/progress")
def get_progress():
    # 和資料庫做互動
    collection = db.forms
    # 使用者學號&姓名
    result = collection.find()

    # 從資料庫動態抓取資料
    # itemvalue = []
    # subtime = []
    # status = []
    progress = []
    len = 0
    # 從資料庫中抓資料做成list
    for items in result:
        if items['studentid'] != session['studentid']:
            continue
        len += 1
        # itemvalue.append(items['fix_subject'])
        # subtime.append(items['submitime'])
        # status.append(items['status'])
        progress.append([items['fix_subject'],items['place'],items['explain'],items['submitime'],items['status']])
    
    # print(itemvalue)
    # print(subtime)
    # print(status)
    print(progress)
    # 再把資料轉成json後傳給前端
    return jsonify(progress)


# 表單驗證、儲存
@app.route('/forms', methods=['POST'])
def forms():
    form = MyForm()

    twtime = pytz.timezone('Asia/Taipei')
    twtime = datetime.now(twtime)
    submitime = twtime.strftime("%Y.%m.%d %H:%M:%S")

    if form.validate_on_submit():
        studentid = session['studentid']
        name = session['name']
        dorm = form.dorm.data
        place = form.place.data
        fixsubject_1 = form.fixsubject_1.data
        fixsubject_2 = form.fixsubject_2.data
        explain = form.explain.data


        forms = db.forms
        forms.insert_one({
            "studentid": studentid,
            "name": name,
            "dorms": dorm,
            "place": place,
            "fix_subject": fixsubject_1,
            "other_fix_subject": fixsubject_2,
            "explain": explain,
            "status": "已提交",
            "submitime": submitime
        })
        # form.dorm.data = ''
        # form.place.data = ''
        # form.fixsubject_1.data = ''
        # form.fixsubject_2.data = ''
        # form.explain.data = ''

        # 刪除資料用
    #     db = client.test
    #     collection = db.forms
    #     result = collection.delete_many({
    #         "name": "傑哥"
    # })
        # print("實際上被刪除的資料",result.deleted_count)

    # 記得重新導向回/member !!
    # 不然用render_template("/member",form=form)會被導到/forms
    return redirect(url_for('member'))


# 管理員登入
@app.route("/manager_signin_page", methods=["POST", "GET"])
def manager_signin_page():
    return render_template('mg_signin.html')


@app.route("/manager_signin", methods=["POST"])
def manager_signin():
    account = request.form["account"]
    password = request.form["password"]
    # 和資料庫做互動
    collection = db.managers
    # 檢查帳號密碼是否正確
    result = collection.find_one({
        "$and": [
            {"account": account},
            {"password": password},
        ]
    })

    # 登入失敗，到錯誤頁面
    if result == None:
        return redirect("/error?msg=帳號或密碼輸入錯誤")
    # 登入成功，在 session 紀錄會員資訊，到會員頁面
    session["account"] = result["account"]
    session["name"] = result["name"]
    print(session['account'])
    return render_template("manager_page.html")


# 管理員註冊
@app.route("/manager_signup_page", methods=["POST"])
def manager_signup_page():
    return render_template('mg_signup.html')


@app.route("/manager_signup", methods=["POST"])
def manager_signup():
    name = request.form['name']
    account = request.form['account']
    password = request.form['password']

    collection = db.managers
    result = collection.find_one({
        "account": account,
    })
    if result != None:
        return redirect("/error?msg=帳號已被註冊")

    collection.insert_one({
        "name": name,
        "account": account,
        "password": password,
    })
    return redirect("/manager_signup_page")


@app.route("/error")
def error():
    message = request.args.get("msg", "發生錯誤")
    return render_template("error.html", message=message)

# 使用者登出


@app.route("/signout")
def signout():
    del session['name']
    del session['studentid']
    return redirect("/")


app.run(
    # host= '0.0.0.0', 任何ip都可訪問
    port=3000, 
    debug=True
    )
