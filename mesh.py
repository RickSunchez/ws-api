import json
from db_connectors import LocalDB

db = LocalDB("local_database.db")

# db.drop()
# exit()

with open("mesh/items.json", "r", encoding="utf-8") as f:
    items = json.loads(f.read())

for item in items:
    db.createItem(
        item["title"], 
        item["description"], 
        item["price"],  
        [item["file"]]
    )

with open("mesh/news.json", "r", encoding="utf-8") as f:
    news = json.loads(f.read())

for n in news:
    db.createNews(
        -2, 
        n["title"], 
        n["description"], 
        [n["file"]]
    )

with open("mesh/users.json", "r", encoding="utf-8") as f:
    users = json.loads(f.read())

for user in users:
    db.newServiceKey(user)
# db.GetItems(count=2, scope=0)

# print(db.GetNews(order_by="date", limit=3))

# db.drop()