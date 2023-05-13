from fastapi import FastAPI
from pymongo import MongoClient, ASCENDING 
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId

app = FastAPI()
client = MongoClient("mongodb://localhost:27017/")
db = client["bookStore"]
collection = db["books"]

class Book(BaseModel):
    book_id: str
    title: str
    author: str
    description: str
    price: int
    stock: int

class SearchPayload(BaseModel):
    searchBy : str
    value: str
    min: str
    max: str

# collection.create_index([('title', 'text')])

# collection.create_index([('author', 'text')])

# collection.create_index([('price', ASCENDING)])

# collection.create_index([('stock', ASCENDING)])


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

@app.get("/books/top-authors")
def get_top_authors():
    pipeline = [
        {"$group": {"_id": "$author", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    result = collection.aggregate(pipeline)
    authors = []
    for doc in result:
        authors.append(doc['_id'])
    return {"authors": authors}
   
    



    

