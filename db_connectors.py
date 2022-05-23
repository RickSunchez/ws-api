import json
import sqlite3
from sqlQuery import *

# fix errors message
# check all responses

NEWS_FILES_FOLDER = "images/items_img/"
ITEMS_FILES_FOLDER = "images/news_img/"

class LocalDB:
    # DB methods
    def __init__(self, filename:str):
        self.db = filename

        self.conn = None
        self.cursor = None

        self.lastID = 0
        
        self.sql(Tables.Users)
        self.sql(Tables.Service)
        self.sql(Tables.Orders)
        self.sql(Tables.Sessions)
        self.sql(Tables.Files)
        self.sql(Tables.News)
        self.sql(Tables.FilesNews)
        self.sql(Tables.Items)
        self.sql(Tables.FilesItems)

    def newConnection(self):
        self.conn = sqlite3.connect(self.db)
        self.cursor = self.conn.cursor()

    def closeConnection(self):
        self.conn.commit()
        self.conn.close()

        self.cursor = None
        self.conn = None

    def sql(self, query:str):
        try:
            self.newConnection()

            result = self.cursor.execute(query)
            answer = result.fetchall()

            self.lastID = self\
                .cursor\
                .execute("SELECT last_insert_rowid()")\
                .fetchone()[0]

            self.closeConnection()
            return answer, False
        except Exception as ex:
            return "", ex

    def drop(self):
        self.sql("DROP TABLE IF EXISTS users")
        self.sql("DROP TABLE IF EXISTS service")
        self.sql("DROP TABLE IF EXISTS orders")
        self.sql("DROP TABLE IF EXISTS sessions")
        self.sql("DROP TABLE IF EXISTS files")
        self.sql("DROP TABLE IF EXISTS news")
        self.sql("DROP TABLE IF EXISTS news_files")
        self.sql("DROP TABLE IF EXISTS items")
        self.sql("DROP TABLE IF EXISTS items_files")

    def GetTableHeaders(self, table_name:str):
        answer, err = self.sql("PRAGMA table_info(%s)" % table_name)
        if err != False: return self.answer(False, {"errror": err.args})

        out = []
        for row in answer: out.append(row[1])

        return self.answer(True, {"fields": out})

    def answer(self, status:bool, message):
        return {"ok": status, "response": message}
    
    def isEmpty(self, answer):
        return (answer is None) or (len(answer) == 0)

    # SERVICE METHODS
    def GetServiceKey(self, api_id:str):
        answer, err = self.sql(Queries.SELECTservice(api_id))
        if err != False: return self.answer(False, {"errror": err.args})

        if self.isEmpty(answer): return self.answer(False, {"errror": "Invalid api_id"})

        return self.answer(True, {"token": answer[0][0]})

    def newServiceKey(self, api_id:str):
        _, err = self.sql(Queries.INSERTservice(api_id))
        if err != False: return self.answer(False, {"errror": err.args})

        return self.answer(True, {"status": "Success"})

    def CheckServiceKey(self, token:str):
        answer, err = self.sql(Queries.SELECTtoken(token))
        if err != False: return self.answer(False, {"errror": err.args})

        if self.isEmpty(answer): return self.answer(False, {"errror": "Invalid service_key"})

        return self.answer(True, {"message": "Success"})

    # USER METHODS
    def CreateUser(self, firstname:str, lastname:str, email:str, password:str):
        isExists, err = self.userExists(email)

        if err != False: return self.answer(False, {"errror": err.args})
        if isExists: return self.answer(False, {"errror": "Email %s alredy taken" % email})

        _, err = self.sql(Queries.INSERTuser(firstname, lastname, email, password))
        if err != False: return self.answer(False, {"errror": err.args})

        return self.answer(True, {"message": "User created"})
        
    def GetUser(self, user_id:int):
        answer, err = self.sql(Queries.SELECTuserById(user_id=user_id))
        if err != False: return self.answer(False, {"errror": err.args})

        return self.answer(True, {
            "user": {
                "user_id": answer[0][0], 
                "first_name": answer[0][1], 
                "last_name": answer[0][2], 
                "email": answer[0][3], 
                "cart": answer[0][4]
            }})

    def userExists(self, email):
        result, err = self.sql(Queries.SELECTuserByEmail(email))

        if err == False:
            return (result is not None) and (len(result) != 0), False
        else:
            return False, err

    def CheckAuth(self, email:str, pass_hash:str):
        answer, err = self.sql(Queries.SELECTuserForAuth(email, pass_hash))
        if err != False: return self.answer(False, {"errror": err.args})

        if self.isEmpty(answer):
            return -1
        else:
            return answer[0][0]
            
    # SESSION METHODS
    def CreateSession(self, user_id:int):
        sql, token = Queries.INSERTsession(user_id)
        _, err = self.sql(sql)
        if err != False: return self.answer(False, {"errror": err.args})

        return self.answer(True, {"token": token})

    def RemoveSession(self, token:str):
        _, err = self.sql(Queries.DELETEsession(token))
        if err != False: return self.answer(False, {"errror": err.args})

        return self.answer(True, {"message": "Session removed"})

    def CheckSession(self, token:str):
        answer, err = self.sql(Queries.SELECTsession(token))
        if err != False: return self.answer(False, {"errror": err.args})

        if self.isEmpty(answer): 
            return self.answer(False, {"message": "Invalid token"}), -1

        return self.answer(True, {"message": "Session checked"}), answer[0][0]
    
    # NEWS METHODS
    def createNews(self, user_id:int, title:str, description:str, files:list):
        _, err = self.sql(Queries.INSERTnews(user_id, title, description))
        if err != False: return self.answer(False, {"errror": err.args})
        
        lastNewsId = self.lastID

        for f in files:
            lastFileId, err = self.insertFile(user_id, f)
            if err != False: return self.answer(False, {"errror": err.args})

            err = self.connectFileWithTable("news_files", lastNewsId, lastFileId)
            if err != False: return self.answer(False, {"errror": err.args})

    def GetNews(self, limit:int=5, order_by:str="date", sort_flag:bool=True):
        if sort_flag:
            sort = "ASC"
        else:
            sort = "DESC"

        answer, err = self.sql(Queries.SELECTnews(limit, order_by, sort))
        if err != False: return self.answer(False, {"errror": err.args})

        out = []
        for row in answer:
            files, err = self.getFilesByObjectId("news_files", row[0])
            if err != False: return self.answer(False, {"errror": err.args})

            out.append({
                "news_id": row[0],
                "user_id": row[1],
                "title": row[2],
                "description": row[3],
                "date": row[4],
                "files": files
            })

        return self.answer(True, {"news": out})

    # ITEMS METHODS
    def createItem(self, title:str, description:str, price:int, files:list):
        _, err = self.sql(Queries.INSERTitem(title, description, price))
        if err != False: return self.answer(False, {"errror": err.args})

        lastItemId = self.lastID

        for f in files:
            lastFileId, err = self.insertFile(-2, f)
            if err != False: return self.answer(False, {"errror": err.args})

            err = self.connectFileWithTable("items_files", lastItemId, lastFileId)
            if err != False: return self.answer(False, {"errror": err.args})
        
    def GetItems(self, count:int, scope:int):
        answer, err = self.sql(Queries.SELECTitems())
        if err != False: return self.answer(False, {"errror": err.args})

        out = []
        for row in answer:
            if row[0] < scope: continue
            if count <= 0: break
            count -= 1

            files, err = self.getFilesByObjectId("items_files", row[0])
            if err != False: return self.answer(False, {"errror": err.args})

            out.append({
                "item_id": row[0],
                "title": row[1],
                "description": row[2],
                "price": row[3],
                "files": files
            })
        
        return self.answer(True, {"items": out})

    def GetItem(self, item_id:list):
        answer, err = self.sql(Queries.SELECTitem(item_id))
        if err != False: return self.answer(False, {"errror": err.args})

        if self.isEmpty(answer): return self.answer(False, "Invalid item_id")
        
        out = []
        for row in answer:
            files, err = self.getFilesByObjectId("items_files", row[0])
            if err != False: return self.answer(False, {"errror": err.args})

            out.append({
                "item_id": row[0],
                "title": row[1],
                "description": row[2],
                "price": row[3],
                "files": files
            })
        
        return self.answer(True, {"items": out})

    # FILES METHODS
    def insertFile(self, user_id:int, filename:str):
        _, err = self.sql(Queries.INSERTfiles(user_id, filename))
        if err != False: return None, err

        return self.lastID, False

    def getFilesByObjectId(self, table_name:str, obj_id:int):
        answer, err = self.sql(Queries.SELECTfilesFromTable(table_name, obj_id))
        if err != False: return None, err

        preDir = {
            "news_files": NEWS_FILES_FOLDER,
            "items_files": ITEMS_FILES_FOLDER
        }

        out = []
        for row in answer:
            filename, err = self.sql(Queries.SELECTfilename(row[0]))
            if err != False: return None, err
            out.append(preDir[table_name] + filename[0][0])

        return out, False

    def connectFileWithTable(self, table_name:str, obj_id:int, file_id:int):        
        _, err = self.sql(Queries.INSERTfileByTable(table_name, obj_id, file_id))
        if err != False: return err

        return False

    # CART METHODS
    def GetCart(self, user_id:int):
        answer, err = self.sql(Queries.SELECTcart(user_id))
        if err != False: return self.answer(False, {"errror": err.args})

        return self.answer(True, {
            "user_id": user_id,
            "cart": answer[0]
        })

    def AddToCart(self, user_id:int, item_id:int):
        answer, err = self.sql(Queries.SELECTcart(user_id))
        if err != False: return self.answer(False, {"errror": err.args})

        cart = json.loads(answer[0][0])
        cart.append(item_id)

        _, err = self.sql(Queries.INSERTcart(user_id, json.dumps(cart)))
        if err != False: return self.answer(False, {"errror": err.args})

        return self.answer(True, {"message": "Success"})

    def RemoveFromCart(self, user_id:int, item_id:int):
        answer, err = self.sql(Queries.SELECTcart(user_id))
        if err != False: return self.answer(False, {"errror": err.args})

        cart = json.loads(answer[0][0])
        if item_id not in cart: return self.answer(False, {"errror": "Item not included"})

        i = cart.index(item_id)
        cart.pop(i)

        _, err = self.sql(Queries.INSERTcart(user_id, json.dumps(cart)))
        if err != False: return self.answer(False, {"errror": err.args})

        return self.answer(True, {"message": "Success"})

    # ORDERS
    def MoveOrder(self, user_id:int):
        answer, err = self.sql(Queries.SELECTcart(user_id))
        if err != False: return self.answer(False, {"errror": err.args})

        cart = answer[0][0]
        if len(json.loads(cart)) == 0: return self.answer(False, {"errror": "Cart is empty"})

        answer, err = self.sql(Queries.INSERTorder(user_id, cart))
        if err != False: return self.answer(False, {"errror": err.args})

        _, err = self.sql(Queries.INSERTcart(user_id, json.dumps([])))
        if err != False: return self.answer(False, {"errror": err.args})

        return self.answer(True, {"message": "Success"})

    def GetOrders(self, user_id:int):
        answer, err = self.sql(Queries.SELECTorders(user_id))
        if err != False: return self.answer(False, {"errror": err.args})

        out = []
        for row in answer:
            out.append({
                "order_id": row[0],
                "order_items": json.loads(row[1]),
                "status": row[2]
            })

        return self.answer(True, {
            "user_id": user_id,
            "orders": out
        })

    def RemoveOrder(self, order_id:int):
        _, err = self.sql(Queries.DELETEorder(order_id))
        if err != False: return self.answer(False, {"errror": err.args})

        return self.answer(True, {"message": "Success"})