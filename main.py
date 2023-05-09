from fastapi import FastAPI
import pymongo
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId

app = FastAPI()
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["bookStore"]
collection = db["books"]

class Book(BaseModel):
    book_id: str
    title: str
    author: str
    description: str
    price: int
    stock: int


# Get all books
@app.get("/books")
def index():
    result = collection.find()
    res = []
    for i in result:
        i["_id"] = str(i["_id"])
        res.append(i)
    return JSONResponse(content=res)

#Get book by Id
@app.get("/book/{book_id}")
async def getbookById(book_id:str):
    result = collection.find_one({"_id": ObjectId(book_id)})
    if result:
        result["_id"] = str(result["_id"])
    return result

@app.post("/users")
def create_user(book: Book):
    print(book)
    book_dict = book.dict()
    collection.insert_one(book_dict) # to be checked failure 
    return True

@app.put("/")
def updateBook(book:Book):
    book_dict = book.dict()
    print(book_dict)
    book_id = book_dict["book_id"]
    book_dict.pop("book_id", None)
    book_oid = ObjectId(book_id)
    result = collection.update_one(
        {"_id": book_oid},
        {"$set": book_dict}
    )

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