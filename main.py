from tkinter.font import names

import mysql.connector
from mysql.connector import Error


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Nurul@321",
    database="COMPANY_DB"
)

cur = conn.cursor()

q = "select * from COMPANY_DB.EMPLOYEE"
cur.execute(q)
datas = cur.fetchall()
print(datas)






























# while True:
#     # print("Insert data in MySql database")
#     # print("Employees Details")
#     # E_ID = int(input("Enter ID:"))
#     # name = input("what is your name:")
#     # age = int(input("How older you:"))
#     # department = input("Name of the department:")
#     # salary = float(input("Salary:"))
#     #
#     # sql = "INSERT INTO EMPLOYEE(EMP_ID, NAME, AGE, DEPARTMENT,SALARY) VALUES (%s, %s, %s, %s,%s)"
#     # val = (E_ID, name, age, department,salary)
#     # cursor.execute(sql,val)
#     # conn.commit()
#     #
#     # print("Record inserted successfully.")
#
#     cursor.execute("SELECT * FROM COMPANY_DB.EMPLOYEE")
#     rows = cursor.fetchall()
#
#
#     cursor.close()
#     conn.close()

