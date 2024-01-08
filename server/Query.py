########################################################
#      Will always return list of tuples               #
#      the tuples in the list are itself a tuple       #
#      i.e.                                            #
#      [((), (), ...), ((), (), ...), ... ...]         #
########################################################

from Dbconnection import DBConnection
db = DBConnection()


def database_check(username, email):
    db.cursor.execute(
        f'''
        SELECT username, email
        FROM user_info
        WHERE username = %s
        OR  email = %s;
        ''', (username, email)
    )
    return db.cursor.fetchall()


def valid_login(email, password):
    db.cursor.execute(
        f'''
        SELECT COUNT(*)
        FROM user_info
        WHERE email = %s
        AND password = %s;
        ''', (email, password)
    )
    result = db.cursor.fetchall()
    if len(result):
        return result
    else:
        return []


def create_account(name, username, email, password):
    db.cursor.execute(
        f"""
        INSERT INTO user_info (name, username, email, password)
        VALUES(%s, %s, %s, %s);
        """, (name, username, email, password)
    )
    db.connection.commit()


def eligible_for_deletion(user_id, name, username, email, password):
    db.cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM user_info
        WHERE
            id = %s
            AND name = %s
            AND username = %s
            AND email = %s
            AND password = %s;
        """, (user_id, name, username, email, password)
    )

    result = db.cursor.fetchall()
    if len(result):
        db.cursor.execute(
            f"""
                DELETE FROM user_chat
                WHERE
                    sender_id = %s
                    OR receiver_id = %s;
                """, (user_id, user_id)
        )
        db.connection.commit()
        return result
    else:
        return []


def delete_account(email):
    db.cursor.execute(
        f"""
        DELETE FROM user_info
        WHERE email = %s
        """, (email,)
    )
    db.connection.commit()


def fetch_user_search(name, senderID):
    db.cursor.execute(
        f'''
    SELECT username
    FROM user_info
    WHERE (name LIKE %s
    OR username LIKE %s) AND (NOT id = %s);
    ''', ('%' + name + '%', '%' + name + '%', senderID)
    )
    return db.cursor.fetchall()


def fetch_user(senderID):
    db.cursor.execute(
        f'''
    SELECT username
    FROM user_info
    WHERE NOT id = %s;
    ''', (senderID,)
    )
    return db.cursor.fetchall()


def update_chats(senderID, receiverID, msg):
    db.cursor.execute(
        f"""
        INSERT INTO user_chat(sender_id, receiver_id, message, message_date, message_time, is_taken)
        VALUES(%s, %s, %s, CURRENT_DATE(), CURRENT_TIME(), FALSE);
        """, (senderID, receiverID, msg)
    )
    db.connection.commit()


def get_id_by_email(email):
    db.cursor.execute(
        f"""
        SELECT id
        FROM user_info
        WHERE email = %s;
        """, (email,)
    )
    result = db.cursor.fetchall()
    if result:
        return result
    else:
        return [(-1,)]


def get_id_by_username(username):
    db.cursor.execute(
        f"""
        SELECT id
        FROM user_info
        WHERE username = %s;
        """, (username,)
    )

    result = db.cursor.fetchall()
    if result:
        return result
    else:
        return [(-1,)]


def get_all_by_id(user_id):
    db.cursor.execute(
        f"""
        SELECT id, name, username, email
        FROM user_info
        WHERE id = %s;
        """, (user_id,)
    )
    return db.cursor.fetchall()


def showMessages(senderID, receiverID):
    db.cursor.execute(
        f"""
        SELECT sender_id, message, message_time, message_date
        FROM user_chat
        WHERE
        (sender_id = %s AND receiver_id = %s)
        OR (sender_id = %s AND receiver_id = %s)
        ORDER BY message_date ASC, message_time ASC;
        """, (senderID, receiverID, receiverID, senderID)
    )
    return db.cursor.fetchall()


def look_for_message(receiverId, senderId):
    db.cursor.execute(
        f"""
            SELECT sender_id, message, message_time, message_date
            FROM user_chat
            WHERE sender_id = %s
            AND receiver_id = %s
            AND is_taken = FALSE;
        """, (receiverId, senderId)
    )
    return db.cursor.fetchall()


def message_taken(receiverId, senderId):
    db.cursor.execute(
        f"""
            UPDATE user_chat
            SET is_taken = TRUE
            WHERE sender_id = %s
            AND receiver_id = %s;
        """, (receiverId, senderId)
    )
    db.connection.commit()
