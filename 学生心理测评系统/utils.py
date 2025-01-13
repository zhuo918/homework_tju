import zmail
from config import BaseConfig 
import sqlite3 


def create_user_information():
    """ 
    建立存储用户信息的表格
    """
    with sqlite3.connect(BaseConfig.DATABASE_NAME) as connection:
        sql = """ 
        CREATE TABLE IF NOT EXISTS user_information (
            account VARCHAR(50) NOT NULL PRIMARY KEY,    -- 用户的账户名
            password VARCHAR(50) NOT NULL,   -- 用户的登录密码
            nickname VARCHAR(50) NOT NULL,   -- 用户的昵称
            age INT NOT NULL,    -- 用户的当前年龄
            phone_number VARCHAR(15),   -- 用户的电话号码
            email VARCHAR(30),  -- 用户的电子邮箱地址
            register_date VARCHAR(10),  -- 用户的注册时间
            description TEXT, -- 用户的个人描述
            role VARCHAR(10)    -- 角色
        )
        """
        connection.execute(sql)
        connection.commit()


def create_test_hirstory():
    """ 
    建立存储心理测评历史记录的表格 
    """
    with sqlite3.connect(BaseConfig.DATABASE_NAME) as connection:
        sql = """ 
        CREATE TABLE IF NOT EXISTS test_history (
            account VARCHAR(50),    -- 用户的账户名
            test_id VARCHAR(10),    -- 心理测试的ID 
            test_name VARCHAR(50),  -- 心理测试名称
            test_answers VARCHAR(200),  -- 心理测试填写的答案
            test_date VARCHAR(30)   -- 测试发生的时间
        )
        """
        connection.execute(sql)
        connection.commit()


def create_teacher_information():
    """ 
    建立存储心理咨询师信息的表格 
    """
    with sqlite3.connect(BaseConfig.DATABASE_NAME) as connection:
        sql = """ 
        CREATE TABLE IF NOT EXISTS teacher_information (
            id VARCHAR(20) PRIMARY KEY,    -- ID 
            phone_number VARCHAR(15),   -- 电话号码
            email VARCHAR(30),  -- 电子邮箱地址
            name VARCHAR(10),    -- 姓名
            age INT,    -- 年龄
            work_year INT,   -- 工作经历
            degree VARCHAR(20),    -- 学历
            field VARCHAR(20),  -- 最擅长的领域
            score INT  -- 评分 
        )
        """
        connection.execute(sql)
        connection.commit()


def create_appointment_record():
    """ 
    建立存储心理咨询预约记录的表格 
    """
    with sqlite3.connect(BaseConfig.DATABASE_NAME) as connection:
        sql = """ 
        CREATE TABLE IF NOT EXISTS appointment_record (
            appointment_id VARCHAR(20), -- 预约的ID 
            account VARCHAR(20),    -- 预约学生的账户 
            teacher_id VARCHAR(20), -- 心理咨询师的ID
            date VARCHAR(20),   -- 心理咨询的日期
            time VARCHAR(20)   -- 心理咨询的时间 
        )
        """
        connection.execute(sql)
        connection.commit()


def create_tables():
    """ 
    建立项目所需要的全部数据库表 
    """
    create_user_information()
    create_teacher_information()
    create_test_hirstory()
    create_appointment_record()


def send_mail(target, subject, context):
    try:
        server = zmail.server(BaseConfig.SERVICE_EMAIL, BaseConfig.CODE)
        mail_body = dict(subject=subject, content_text=context)
        server.send_mail(target, mail_body)
    except Exception as error:
        print(error)
        raise Exception("服务器故障")