from flask import Flask, request, jsonify, send_from_directory, make_response
from flask import render_template 
import sqlite3
import numpy as np 
from faker import Faker
import os 
import datetime
from model import * 
import pickle
from blueprints.login import * 
from blueprints.appointment import * 
from utils import * 
from lightgbm.sklearn import LGBMClassifier
from matplotlib import pyplot as plt 
plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False


app = Flask(__name__) # PORT：http://127.0.0.1:5000/
# 这里不知道使用什么数据库,为了便于演示使用轻量级本地数据库SQLite3
# (注：大型程序里面一般使用MySQL等,但是大型程序一般不会使用Flask作为后端)
DATABASE_NAME = "database.sqlite3"
SERVICE_EMAIL = "477512060@qq.com"
CODE = "etxbsckmfyerbgch"
with open("model1.pickle", "rb") as file:
    model1: LGBMClassifier = pickle.load(file)
model2: LGBMClassifier = pickle.load(open("model2.pickle", "rb"))
model3: LGBMClassifier = pickle.load(open("model3.pickle", "rb"))


@app.route("/sendEmail", methods=["POST"])
def send_email_to_teacher():
    type_ = request.form.get("type")
    teacher_id = request.form.get("id")
    account = request.form.get("account")
    with sqlite3.connect(DATABASE_NAME) as connection:
        sql = f"SELECT email FROM teacher_information WHERE id = '{teacher_id}'"
        teacher_email = connection.execute(sql).fetchone()[0]
        sql = f"SELECT email FROM user_information WHERE account = '{account}'"
        student_email = connection.execute(sql).fetchone()[0]
    if type_ == "plan":
        date = request.form.get("date")
        time = request.form.get("time")
        message = f"学生预约申请,日期:{date},时间:{time},预约学生邮箱:{student_email}"
        try:
            send_mail(teacher_email, "线下心理咨询预约", context=message)
        except Exception as error:
            print(error)
            return jsonify({"success": False})
        else:
            return jsonify({"success": True})
    elif type_ == "ask":
        content = request.form.get("content")
        message = f"心里咨询,内容:{content},请回复到学生邮箱:{student_email}"
        try:
            send_mail(teacher_email, "在线心理咨询", context=message)
        except Exception as error:
            print(error)
            return jsonify({"success": False})
        else:
            return jsonify({"success": True})
    

@app.route("/")
def index():
    return render_template("login.html")


@app.route("/system")
def system():
    return render_template("system.html")


@app.route("/manager")
def manager():
    return render_template("manager.html")


@app.route("/getInformationForManager", methods=["GET"])
def get_information_for_manager():
    response = {"userDataTable": []}
    with sqlite3.connect(DATABASE_NAME) as connection:
        sql = "SELECT account,nickname,phone_number,email FROM user_information WHERE role='user'"
        results = connection.execute(sql).fetchall()
        for account, nickname, phone_number, email in results:
            obj = {"account": account, "nickname": nickname, "phoneNumber": phone_number, "email": email}
            sql = f"SELECT * FROM test_history WHERE account='{account}'"
            obj["count"] = len(connection.execute(sql).fetchall())
            response["userDataTable"].append(obj)
    return jsonify(response)

@app.route("/getTeacherList")
def get_teacher_list():
    response = {"teacherList": []}
    with sqlite3.connect(DATABASE_NAME) as connection:
        sql = "SELECT name,age,work_year,id,email,score,field,degree FROM teacher_information"
        for name,age,work_year,id_,email,score,field,degree in connection.execute(sql).fetchall():
            response["teacherList"].append(dict(name=name, age=age, work_year=work_year, id=id_, email=email, score=score, field=field, degree=degree))
    return jsonify(response)


@app.route("/addTeacher", methods=["POST"])
def add_teacher():
    response = {} 
    with sqlite3.connect(DATABASE_NAME) as connection:
        # 首先,生成一个ID
        length = len(connection.execute("SELECT * FROM teacher_information").fetchall())
        id_ = f"Teacher{length + 1}"
        name = request.form.get("name")
        age = request.form.get("age")
        work_year = request.form.get("workYear")
        email = request.form.get("email")
        phone_number = request.form.get("phoneNumber")
        degree = request.form.get("degree")
        field = request.form.get("field")
        sql = f""" 
        INSERT INTO teacher_information VALUES (
            '{id_}', 
            '{phone_number}',
            '{email}',
            '{name}', 
            {age},
            {work_year},
            '{degree}',
            '{field}',
            0
        )
        """
        try: connection.execute(sql)
        except Exception as error:
            print(error)
            response["success"] = False 
        else: response["success"] = True
        return jsonify(response)

@app.route("/deleteTeacher", methods=["POST"])
def delete_teacher():
    id_ = request.form.get("id")
    response = {}
    with sqlite3.connect(DATABASE_NAME) as connection:
        sql = f"DELETE FROM teacher_information WHERE id='{id_}'"
        try: connection.execute(sql)
        except Exception: response["success"] = False
        else: response["success"] = True
    return response


@app.route("/getInformation", methods=["GET"])
def get_information():
    """ 
    当用户登录成功的时候，需要加载个人信息界面，前端需要从浏览器上获取登录信息
    个人信息界面通过浏览器上记录的登录信息向后端发送请求，得到完整的信息
    """
    account = request.args.get("account")
    with sqlite3.connect(DATABASE_NAME) as connection:
        sql = f"SELECT nickname, age, phone_number, email, description FROM user_information WHERE account = '{account}'"
        nickname, current_age, phone_number, email, description = connection.execute(sql).fetchall().pop() 
    return jsonify({"nickname": nickname, "currentAge": current_age, "phoneNumber": phone_number, "email": email, "description": description})


@app.route("/getHistory", methods=["GET"])
def get_history():
    account = request.args.get("account")
    with sqlite3.connect(DATABASE_NAME) as connection:
        results = connection.execute(f"SELECT test_id, test_name, test_date FROM test_history WHERE account = '{account}'").fetchall()
    response = {"dataTable": []} 
    for test_id, test_name, test_date in results:
        response["dataTable"].append({"id": test_id, "name": test_name, "date": test_date})
    return jsonify(response)


@app.route("/searchHistoryDetails", methods=["GET"])
def search_history_details():
    test_id = request.args.get("testid")
    account = request.args.get("account")
    with sqlite3.connect(DATABASE_NAME) as connection:
        sql = f"SELECT test_answers, test_name FROM test_history WHERE account='{account}' AND test_id='{test_id}'"
        print(sql)
        result = connection.execute(sql).fetchall()
    answers, name = result.pop(0)
    answers = answers.split(",")
    if name == "基于机器学习技术的多维度心理测试":
        history = questions1.copy()
        for i in range(len(history)):
            history[i]["userAnswer"] = answers[i]
    return jsonify({"data": history, "name": name})


@app.route("/deleteById", methods=["POST"])
def delete_by_id():
    test_id = request.form.get("testid")
    response = dict()
    sql = f"DELETE FROM test_history WHERE test_id = '{test_id}'"
    with sqlite3.connect(DATABASE_NAME) as connection:
        try:
            connection.execute(sql)
        except Exception as error:
            print(error)
            response["success"] = False 
        else:
            response["success"] = True
    return jsonify(response)


@app.route("/searchHistory", methods=["POST"])
def search_history():
    account = request.form.get("account")
    test_name = request.form.get("testName")
    start_date, end_date = request.form.get("startDate"), request.form.get("endDate")
    search_by_name = False
    if test_name in {"machineLearningTestV1"}:
        search_by_name = True
        if test_name == "machineLearningTestV1":
            test_name = "基于机器学习技术的多维度心理测试"
    with sqlite3.connect(DATABASE_NAME) as connection:
        sql = f"""
        SELECT test_id, test_name, test_date FROM test_history
        WHERE account = '{account}' 
        AND test_date > '{start_date}' 
        AND test_date < '{end_date}' 
        """
        if search_by_name:
            sql += f"\n        AND test_name = '{test_name}'"
        results = connection.execute(sql).fetchall()
    response = {"dataTable": []} 
    for test_id, test_name, test_date in results:
        response["dataTable"].append({"id": test_id, "name": test_name, "date": test_date})
    return jsonify(response)


@app.route("/changeUserInformation", methods=["POST"])
def change_user_information():
    account = request.form.get("account")
    nickname = request.form.get("newNickname")
    age = request.form.get("currentAge")
    phone_number = request.form.get("newPhoneNumber")
    email = request.form.get("newEmail")
    description = request.form.get("description")
    with sqlite3.connect(DATABASE_NAME) as connection:
        response = {} 
        sql = f""" 
        UPDATE user_information SET 
        nickname='{nickname}',
        age={age},
        phone_number='{phone_number}',
        email='{email}',
        description='{description}'
        WHERE account = '{account}'
        """
        try:
            connection.execute(sql)
        # 系统故障,无法正确更改数据库
        except Exception as error:
            response["success"] = False
            print(error)
        else:
            connection.commit()
            response["success"] = True
    return response 


@app.route("/beginTesting", methods=["GET"])
def get_test_data():
    """ 前端传入GET请求,后端解析GET请求的参数并返回前端所需要的心理测评问卷数据 """
    test_name = request.args.get("testName")
    if test_name == "machineLearningTestV1":
        test_data = questions1.copy()
        test_name = "基于机器学习技术的多维度心理测试"
    for i in range(len(test_data)):
        test_data[i]["userAnswer"] = "" 
    response = dict(data=test_data, name=test_name)
    return jsonify(response)


@app.route("/testingResult", methods=["POST"])
def analysis_testing_result():
    """ 
    接受后端发送的POST请求，使用训练好的机器学习模型对前端发来的问卷结果进行计算
    该函数做了下面的3个事情:
    (1).调用后端的机器学习模型预测心理测评结果
    (2).基于模板和数据可视化生成心理测评结果，并保存在后端文件系统
    (3).将心理测试历史记录放到数据库
    此外，后端向前端返回响应，success表示后端是否成功执行了步骤(1),(2),(3)
    """
    response = dict() 
    account = request.form.get("account")
    test_name = request.form.get("testName")
    test_date = datetime.date.today()
    answers = request.form.get("answers")
    answers_string = answers
    answers = list(map(int, answers.split(","))) if isinstance(answers, str) else answers

    # 根据数据库已经有的测评历史记录数量生成一个测评ID
    sql = f"SELECT * FROM test_history WHERE account = '{account}'"
    with sqlite3.connect(DATABASE_NAME) as connection:
        test_id = f"TEST{len(connection.execute(sql).fetchall())}"

    try:
        # 尝试将心理测评记录计算并保存到文件系统和数据库
        if test_name == "machineLearningTestV1":
            test_name = "基于机器学习技术的多维度心理测试"
            if not os.path.exists(f"static\{account}"):
                os.mkdir(f"static\{account}")
            if not os.path.exists(f"static\{account}\{test_id}"):
                os.mkdir(f"static\{account}\{test_id}")
            # 获取用Numpy表示的特征向量
            feature_vector = np.array([answers])

            # 获得预测概率结果,绘制分析结果的数据可视化图表和心理测评报告模板,并存入服务器端的文件系统（File System）
            result1 = model1.predict_proba(feature_vector)[0]
            plt.figure(figsize=(8, 3))
            plt.bar(x=["低水平焦虑", "中水平焦虑", "高水平焦虑"], height=result1)
            plt.xlabel("测评结果等级")
            plt.ylabel("测评结果等级的概率分布情况")
            plt.title("焦虑指标测试结果的可视化图")
            plt.tight_layout()
            plt.savefig(f"static\{account}\{test_id}\Result1.jpg")
            plt.clf()
            with open(f"static\{account}\{test_id}\Result1.txt", mode="w", encoding="utf-8") as file:
                file.write(result_template1[result1.argmax()])
            result2 = model1.predict_proba(feature_vector)[0]
            plt.bar(x=["低水平抑郁", "中水平抑郁", "高水平焦虑"], height=result2)
            plt.xlabel("测评结果等级")
            plt.ylabel("测评结果等级的概率分布情况")
            plt.title("抑郁指标测试结果的可视化图")
            plt.tight_layout()
            plt.savefig(f"static\{account}\{test_id}\Result2.jpg")
            plt.clf()
            with open(f"static\{account}\{test_id}\Result2.txt", mode="w", encoding="utf-8") as file:
                file.write(result_template2[result2.argmax()])
            result3 = model1.predict_proba(feature_vector)[0]
            plt.bar(x=["低水平压力", "中水平压力", "高水平压力"], height=result3)
            plt.xlabel("测评结果等级")
            plt.ylabel("测评结果等级的概率分布情况")
            plt.title("压力指标测试结果的可视化图")
            plt.savefig(f"static\{account}\{test_id}\Result3.jpg")
            plt.tight_layout()
            plt.clf()
            with open(f"static\{account}\{test_id}\Result3.txt", mode="w", encoding="utf-8") as file:
                file.write(result_template3[result3.argmax()])
        
        # 将心理测评结果保存至数据库
        with sqlite3.connect(DATABASE_NAME) as connection:
            sql = f""" 
            INSERT INTO test_history VALUES (
            '{account}',
            '{test_id}',
            '{test_name}',
            '{answers_string}',
            '{test_date}'
            )
            """ 
            connection.execute(sql)
            connection.commit()
    except Exception as error:
        response["success"] = False 
        print(error)
    else:
        response["success"] = True
    return jsonify(response)


@app.route("/getResult", methods=["GET"])
def get_text_result():
    account = request.args.get("account")
    test_id = request.args.get("testid")
    response = {"textList": [], "imageScrList": []}
    try:
        for i in range(3):
            with open(f"static\{account}\{test_id}\Result{i+1}.txt", mode="r", encoding="utf-8") as file:
                response["textList"].append(file.read())
            response["imageScrList"].append(f"http://127.0.0.1:5000/getImage/{account}/{test_id}/Result{i+1}.jpg")
        response["success"] = True
        return jsonify(response)
    except Exception as error:
        print(error)
        response["success"] = False
        return jsonify(response)

@app.route('/getImage/<account>/<testid>/<filename>', methods=["GET"])  
def get_image(account, testid, filename):  
    print(f"{account}\{testid}\{filename}")
    return send_from_directory(f"static/{account}/{testid}", filename, as_attachment=False)

if __name__ == "__main__":
    # 建立所需要的数据库表
    create_tables()
    # 注册用户登录的蓝图
    app.register_blueprint(login_blueprint, url_prefix="/login")
    # 注册心里预约相关的蓝图 
    app.register_blueprint(appointment_blueprint, url_prefix="/appointment")
    app.run(debug=True)
