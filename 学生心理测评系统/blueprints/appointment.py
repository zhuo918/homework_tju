from config import BaseConfig
from flask import Blueprint, request, jsonify
import sqlite3
from utils import send_mail 

appointment_blueprint = Blueprint("appointment", __name__)


@appointment_blueprint.route("/getAppointmentRecord", methods=["GET"])
def get_appointment_record():
    """ 
    处理前端向后端发送的GET请求,将appointment_record中全部数据返回给前端 
    """
    account = request.args.get("account") 
    response = {"appointmentRecord": []} 
    with sqlite3.connect(BaseConfig.DATABASE_NAME) as connection:
        try:
            results = connection.execute(f"SELECT appointment_id,teacher_id,date,time FROM appointment_record WHERE account='{account}'").fetchall()
            for appointment_id, teacher_id, date, time in results:
                obj = {"appointmentID": appointment_id, "teacherID": teacher_id, "date": date, "time": time}
                response["appointmentRecord"].append(obj)
        except Exception as error:
            print(error)
            response["success"] = False
        else:
            response["success"] = True 
    return jsonify(response)


@appointment_blueprint.route("/makeAppointment", methods=["POST"])
def make_appointment():
    """ 
    学生线下心理咨询预约的逻辑
    """
    date = request.form.get("appointmentDate")
    time = request.form.get("appointmentTime")
    teacher_id = request.form.get("appointmentTeacherID")
    account = request.form.get("account")
    response = {}

    with sqlite3.connect(BaseConfig.DATABASE_NAME) as connection:
        # 找到对应心理咨询师的邮箱
        teacher_email = connection.execute(
            "SELECT email FROM teacher_information WHERE id=?", (teacher_id,)
        ).fetchone()[0]
        student_email = connection.execute(
            "SELECT email FROM user_information WHERE account=?", (account,)
        ).fetchone()[0]
        count = connection.execute(
            "SELECT COUNT(*) FROM appointment_record WHERE account=?", (account,)
        ).fetchone()[0]
        appointment_id = f"Appointment{count + 1}"

        try:
            context = f"线下心理咨询预约申请[ID:{appointment_id}],日期:{date},时间:{time},请回复至学生邮箱:{student_email}"
            send_mail(teacher_email, "心理咨询预约申请", context)
        except Exception as error:
            print(error)
            response["success"] = False
            response["message"] = "心理咨询预约邮箱发送失败"
        else:
            # 邮箱发送成功，将预约信息插入到 appointment_record 数据库
            sql = """INSERT INTO appointment_record VALUES (?, ?, ?, ?, ?)"""
            try:
                connection.execute(sql, (appointment_id, account, teacher_id, date, time))
            except Exception as error:
                print(error)
                response["success"] = False
                response["message"] = "将心理咨询预约信息插入到数据库失败"
            else:
                response["success"] = True
                connection.commit()

    return jsonify(response)


@appointment_blueprint.route("/changeAppointment", methods=["POST"])
def change_appointment():
    appointment_id = request.form.get("appointmentID")
    account = request.form.get("account")
    date = request.form.get("date")
    time = request.form.get("time")
    response = {} 
    with sqlite3.connect(BaseConfig.DATABASE_NAME) as connection:
        sql = f"""UPDATE appointment_record SET
        date = '{date}',
        time = '{time}'
        WHERE account='{account}' AND appointment_id='{appointment_id}'
        """
        try:
            connection.execute(sql)
        except Exception as error:
            print(error)
            response["success"] = False
        else:
            response["success"] = True
            connection.commit()
    return jsonify(response)


@appointment_blueprint.route("/deleteAppointment", methods=["POST"])
def delete_appointment():
    appointment_id = request.form.get("appointmentID")
    account = request.form.get("account")
    response = {} 
    with sqlite3.connect(BaseConfig.DATABASE_NAME) as connection:
        # 得到预约记录中心理咨询师的ID 
        teacher_id = connection.execute(f"SELECT teacher_id FROM appointment_record WHERE appointment_id='{appointment_id}'").fetchone()[0] 
        # 得到心理咨询师的邮箱 
        teacher_email = connection.execute(f"SELECT email FROM teacher_information WHERE id='{teacher_id}'").fetchone()[0]
        student_email = connection.execute(f"SELECT email FROM user_information WHERE account='{account}'").fetchone()[0]
        try:
            subject = "[心理咨询取消申请]"
            context = f"线下心理咨询取消预约申请[ID:{appointment_id}],请回复至学生邮箱:{student_email}"
            send_mail(teacher_email, subject, context)
        except Exception as error:
            print(error)
            response["success"] = False 
            response["message"] = "向心理咨询师发送邮箱时出现错误" 
        else:
            # 邮箱发送成功后,在数据库中删除心理咨询预约记录 
            sql = f"DELETE FROM appointment_record WHERE appointment_id='{appointment_id}' AND account={account}'"
            try:
                connection.execute(sql)
            except Exception as error:
                print(error)
                response["success"] = False 
                response["message"] = "在数据库中删除预约信息时出错"
            else:
                response["success"] = True
    return jsonify(response) 