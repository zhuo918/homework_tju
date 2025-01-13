from flask import Blueprint, request, jsonify 
import sqlite3
from config import BaseConfig 


login_blueprint = Blueprint("login", __name__)


@login_blueprint.route("/login", methods=["POST"])
def login():
    account = request.form.get("account")
    password = request.form.get("password")
    role = request.form.get("role")
    with sqlite3.connect(BaseConfig.DATABASE_NAME) as connection:
        sql = f"SELECT password FROM user_information WHERE account='{account}' AND role='{role}'"
        results = connection.execute(sql).fetchall()
    response = {} 
    # 如果当前用户名不存在 
    if len(results) == 0:
        response["success"] = False
        response["message"] = "当前用户名不存在,请确定是否已经注册"
    else:
        searched_password = results[0][0]
        if searched_password == password:
            response["success"] = True
        # 密码错误
        else:
            response["success"] = False
            response["message"] = "密码错误,请重新输入"
    return jsonify(response)


@login_blueprint.route("/test", methods=["GET"])
def test():
    return 111


@login_blueprint.route("/register", methods=["POST"])
def register():
    account = request.form.get("account")  # 获取要注册的账户
    password = request.form.get("password")  # 获取要注册的密码
    nickname = request.form.get("nickname")  # 要注册的用户名称
    print(nickname)
    age = int(request.form.get("age"))  # 当前注册者的年龄
    role = request.form.get("role")
    response = {} 
    with sqlite3.connect(BaseConfig.DATABASE_NAME) as connection:
        sql = "SELECT account FROM user_information"
        accounts = [item[0] for item in connection.execute(sql).fetchall()]
        if account not in accounts:
            response["success"] = True
            sql = f"INSERT INTO user_information VALUES ('{account}','{password}','{nickname}','{age}', '','','','','{role}')"
            connection.execute(sql)
            connection.commit()
        else:
            response["success"] = False
    return jsonify(response)