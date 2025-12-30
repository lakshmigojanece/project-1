


import mysql.connector

database = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='earthquake'
)

cursorobj = database.cursor()
url= 101,24/04/25,0812.25,north & south, east and west, 10.00, 100, magearthquake, chennai,tamilnadu,2,0.88, 10.00,200,10.00,98.00,200,chennai,magsourdce,onetypes,22,deldhi,black
database.commit()
database.close()








