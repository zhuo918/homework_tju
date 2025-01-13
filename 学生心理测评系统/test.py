from config import BaseConfig 
from faker import Faker 
import sqlite3

def test_user_information():
    # 建立保存用户信息的数据库表格
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
            role VARCHAR(10),    -- 角色
            grade VARCHAR(10),  -- 用户的年级
        )
        """
        connection.execute(sql)
        connection.commit()