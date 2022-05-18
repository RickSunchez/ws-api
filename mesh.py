import json
from db_connectors import LocalDB

db = LocalDB("local_database.db")

# db.drop()
# exit()

# db.newServiceKey("wsr-aaa-bbb")

# db.CreateUser("Имя", "Фамилия", "email", "пароль")
# print(db.GetUser(1))
# print(db.GetTableHeaders("users"))

# print(db.getNewsFiles(6))

# db.createNews(1, "Заголовок1", "Описание1", ["file1", "file2"])
# db.createNews(1, "Заголовок2", "Описание2", ["file3", "file4"])
# db.createNews(1, "Заголовок3", "Описание3", ["file5", "file6"])
# db.createNews(1, "Заголовок4", "Описание4", ["file7", "file8"])
# db.createNews(1, "Заголовок5", "Описание5", ["file9", "file0"])

# db.createItem("Товар1", "Описание1", 123,  ["litem1", "ritem1"])
# db.createItem("Товар2", "Описание2", 1234, ["litem2", "ritem2"])
# db.createItem("Товар3", "Описание3", 22,   ["litem3", "ritem3"])
# db.createItem("Товар4", "Описание4", 15,   ["litem4", "ritem4"])
# db.createItem("Товар5", "Описание5", 4141, ["litem5", "ritem5"])

with open("mesh/items.json") as f:
    items = json.loads(f.read())

for item in items:
    db.createItem(
        item["title"], 
        item["description"], 
        item["price"],  
        [item["file"]]
    )

with open("mesh/news.json") as f:
    news = json.loads(f.read())

for n in news:
    db.createNews(
        -2, 
        n["title"], 
        n["description"], 
        [n["file"]]
    )

with open("mesh/users.json") as f:
    users = json.loads(f.read())

for user in users:
    db.newServiceKey(user)
# db.GetItems(count=2, scope=0)

# print(db.GetNews(order_by="date", limit=3))

# db.drop()