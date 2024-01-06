import mysql.connector


class DBConnection:
    try:
        connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="3378145",
        # password="IATPOMOKaz9@",
        database="db_bit_talker"
        )
        cursor = connection.cursor()

    except:
        print("BitTalker can't be reached right now!")


