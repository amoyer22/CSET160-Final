import mysql.connector

db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "cset155",
    "database": "online_data"
}
try:
    connection = mysql.connector.connect(**db_config)
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)
except Exception as e:
    print("Error while connecting to MySQL", e)
def connect_to_database():
    return mysql.connector.connect(**db_config)


