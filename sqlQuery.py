import calendar
from datetime import datetime, timedelta
import hashlib
import random
import secrets


class Tables:
    Users:str = """
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            password TEXT,
            cart TEXT
        )
    """

    Sessions:str = """
        CREATE TABLE IF NOT EXISTS sessions(
            session_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            session_token TEXT,
            expires_in DATE
        )
    """

    Service:str = """
        CREATE TABLE IF NOT EXISTS service(
            service_id INTEGER PRIMARY KEY,
            service_key TEXT,
            api_id TEXT
        )
    """

    Orders:str = """
        CREATE TABLE IF NOT EXISTS orders(
            order_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            order_items TEXT,
            status INTEGER
        )
    """

    Files:str = """
        CREATE TABLE IF NOT EXISTS files(
            file_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            filename TEXT
        )
    """

    News:str = """
        CREATE TABLE IF NOT EXISTS news(
            news_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            description TEXT,
            date DATETIME
        )
    """

    FilesNews:str = """
        CREATE TABLE IF NOT EXISTS news_files(
            news_id INTEGER,
            file_id INTEGER
        )
    """

    Items:str = """
        CREATE TABLE IF NOT EXISTS items(
            item_id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            price INTEGER
        )
    """

    FilesItems:str = """
        CREATE TABLE IF NOT EXISTS items_files(
            item_id INTEGER,
            file_id INTEGER
        )
    """

class Queries:
    # SERVICE
    def SELECTservice(api_id:str):
        return """
            SELECT service_key FROM service
            WHERE api_id="%s"
        """ % api_id

    def INSERTservice(api_id:str):
        token = secrets.token_hex(nbytes=16)
        return """
            INSERT INTO service (service_key, api_id)
            VALUES ("%s", "%s")
        """ % (token, api_id)

    def SELECTtoken(token:str):
        return """
            SELECT service_id FROM service
            WHERE service_key="%s"
        """ % token
    # USERS
    def INSERTuser(firstname:str, lastname:str, email:str, password:str):
        return """
            INSERT INTO users (first_name,last_name,email,password,cart)
            VALUES ("%s", "%s", "%s", "%s", "[]")
        """ % (firstname, lastname, email, password)

    def SELECTuserById(user_id:int):
        return """
            SELECT user_id, first_name, last_name, email, cart
            FROM users WHERE user_id=%d
        """ % user_id
    
    def SELECTuserByEmail(email:str):
        return """
            SELECT * FROM users WHERE email="%s"
        """ % email

    def SELECTuserForAuth(email:str, pass_hash:str):
        return """
            SELECT user_id
            FROM users 
            WHERE email="%s" AND password="%s"
        """ % (email, pass_hash)
    
    # SESSIONS
    def INSERTsession(user_id:int):
        date = datetime.now()
        month = calendar.monthrange(date.year, date.month)[1]
        date += timedelta(days=month)

        expiresIn = date.strftime("%Y-%m-%d %H:%M:%S")

        token = secrets.token_hex(nbytes=8)

        return """
            INSERT INTO sessions (user_id, session_token, expires_in)
            VALUES (%d, "%s", "%s")
        """ % (user_id, token, expiresIn), token

    def DELETEsession(token:str):
        return """
            DELETE FROM sessions
            WHERE session_token="%s"
        """ % token

    def SELECTsession(token:str):
        return """
            SELECT user_id FROM sessions
            WHERE session_token="%s"
        """ % token
        
    # NEWS
    def INSERTnews(user_id:int, title:str, description:str):
        now = datetime.now()
        formatNow = now.strftime("%Y-%m-%d %H:%M:%S")
        return """
            INSERT INTO news (user_id, title ,description, date)
            VALUES (%d, "%s", "%s", "%s")
        """ % (user_id, title, description, formatNow)

    def SELECTnews(limit:int, order_by:str, sort:str):
        return """
            SELECT * FROM news
            ORDER BY %s %s
            LIMIT %d
        """ % (order_by, sort, limit)  

    # FILES
    def INSERTfiles(user_id:int, filename:str):
        return """
            INSERT INTO files (user_id, filename)
            VALUES (%d, "%s")
        """ % (user_id, filename)

    def SELECTfilename(file_id:int):
        return """
            SELECT filename FROM files
            WHERE file_id=%d
        """ % (file_id)

    def SELECTfilesFromTable(table:str, obj_id:int):
        fields = {
            "news_files": "news_id",
            "items_files": "item_id"
        }
        return """
            SELECT file_id FROM %s
            WHERE %s=%d
        """ % (table, fields[table], obj_id)

    def INSERTfileByTable(table_name:str, obj_id:int, file_id:int):
        return """
            INSERT INTO %s
            VALUES (%d, %d)
        """ % (table_name, obj_id, file_id)

    # ITEMS
    def INSERTitem(title:str, description:str, price:int):
        return """
            INSERT INTO items (title, description, price)
            VALUES ("%s", "%s", %d)
        """ % (title, description, price)

    def SELECTitems():
        return """
            SELECT * FROM items
        """
    
    def SELECTitem(item_ids:list):
        return """
            SELECT * FROM items
            WHERE item_id IN (%s)
        """ % (",".join(item_ids))

    # CART
    def SELECTcart(user_id:int):
        return """
            SELECT cart FROM users
            WHERE user_id=%d
        """ % user_id

    def INSERTcart(user_id:int, cart:str):
        return """
            UPDATE users
            SET cart="%s"
            WHERE user_id=%d   
        """ % (cart, user_id)

    # ORDERS
    def INSERTorder(user_id:int, order:str):
        return """
            INSERT INTO orders (user_id, order_items, status)
            VALUES (%d, "%s", 0)
        """ % (user_id, order)

    def SELECTorders(user_id:int):
        return """
            SELECT order_id, order_items, status 
            FROM orders
            WHERE user_id=%d
        """ % user_id

    def DELETEorder(order_id:int):
        return """
            DELETE FROM orders
            WHERE order_id=%d
        """ % order_id