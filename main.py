from fastapi import FastAPI
from pymongo import MongoClient, ASCENDING, IndexModel
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId
from pymongo.errors import WriteError
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()
client = MongoClient("mongodb://localhost:27017/")
db = client.bookStore

result = db.command({
    "collMod": "books",
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["title", "author"],
            "properties": {
                "title": {
                    "bsonType": "string"
                },
                "author": {
                    "bsonType": "string"
                },
                "price": {
                "type": "number",
                "minimum": 0,
                "maximum": 1000,
                "exclusiveMaximum": False,
                "exclusiveMinimum": False
                }
            }
        }
    },
    "validationLevel": "strict",
    "validationAction": "error"
})

collection = db["books"]


index_model = IndexModel("author")
collection.create_indexes([index_model])

class Book(BaseModel):
    book_id: str
    title: str = Field(..., min_length=1, max_length=50)
    author: str
    description: str
    price: int = Field(..., gt=0)
    stock: int = Field(..., gt=0)
    sold_items: int = Field(..., gt=0)

class SearchPayload(BaseModel):
    searchBy : str
    value: str
    min: str
    max: str

@app.get("/books")
def index():
    result = collection.find()
    res = []
    for i in result:
        i["_id"] = str(i["_id"])
        res.append(i)
    return JSONResponse(content=res)

@app.get("/book/{book_id}")
async def getbookById(book_id:str):
    result = collection.find_one({"_id": ObjectId(book_id)})

    if result:
        result["_id"] = str(result["_id"])
    return result

@app.post("/book")
def create_user(book: Book):
    print(book)
    book_dict = book.dict()
    try:
        collection.insert_one(book_dict) # to be checked failure 
    except WriteError as w:
        return f"Saving record failed {w}"
    return True

@app.put("/")
def updateBook(book:Book):
    book_dict = book.dict() 
    print(book_dict)
    book_id = book_dict["book_id"]
    book_dict.pop("book_id", None)
    book_oid = ObjectId(book_id)

    try:
        result = collection.update_one(
            {"_id": book_oid},
            {"$set": book_dict}
        )
    except WriteError as w:
        print(f"Update book failed {w}")

    if result.modified_count == 1:
        return {"message": "Book updated successfully"}
    else:
        return {"message": "Book not found"}

@app.delete("/books/{book_id}")
def deleteBook(book_id: str):
    result = collection.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count == 1:
        return {"message": f"Book with ID {book_id} has been deleted."}
    else:
        return {"message": "Book not found."}
    
@app.get("/search")
def search(searchPayload: SearchPayload):
    match searchPayload.searchBy:
        case "author":
            print(searchPayload)
            result = collection.find({ "author": { "$eq": searchPayload.value } })
        case "title":
            result = collection.find({ "title": { "$eq": searchPayload.value } })
        case "price":
            result = collection.find({ "price": { "$lt": int(searchPayload.max), "$gt": int(searchPayload.min) } })
        case _:
            return "Deafult case"
    res = []
    for i in result:
        print("helo")
        i["_id"] = str(i["_id"])
        res.append(i)
    return JSONResponse(content=res)

@app.get("/books/top5authors")
def get_top_authors():
    pipeline = [
        {"$group": {"_id": "$author", "count": {"$sum": 2}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    result = collection.aggregate(pipeline)
    authors = []
    for doc in result:
        authors.append(doc['_id'])
    return {"authors": authors}

@app.get("/books/top-selling")
async def get_top_selling_books():
    pipeline = [
        {"$group": {"_id": "$title", "total_sold": {"$sum": "$sold_items"}}},
        {"$sort": {"total_sold": 1}},
        {"$limit": 5}
    ]
    result = collection.aggregate(pipeline)
    books = []
    for doc in result:
        books.append(doc['_id'])
    return {"books": books}

@app.get("/books/count")
async def get_books_count():
    count = collection.count_documents({})
    return {"count": count}

@app.post("/books/purchase/{book_id}")
def purchaseBook(book_id: str):
    query = {"_id": ObjectId(book_id)}
    update = {"$inc": {"sold_items": 1, "stock": -1}}
    try:
        collection.update_one(query, update)
    except WriteError as e:
        print(f"Purchase failed {e}")
        return False
    return True



   
    



    

