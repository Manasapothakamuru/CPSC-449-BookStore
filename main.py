from fastapi import FastAPI, HTTPException
from pymongo import MongoClient, ASCENDING, IndexModel
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId
from pymongo.errors import WriteError
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# Mongo connection
async def connect_to_mongodb():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    return client

@app.on_event("startup")
async def startup_event():
    app.mongodb_client = await connect_to_mongodb()
    await create_indexes()

@app.on_event("shutdown")
async def shutdown_event():
    app.mongodb_client.close()

# indexing fields
async def create_indexes():
    collection = app.mongodb_client.bookStore.books
    await collection.create_index("title")
    await collection.create_index("author")


#Pydantic Model with data validations
class Book(BaseModel):
    book_id: str
    title: str = Field(..., min_length=1, max_length=50)
    author: str = Field(..., min_length=1, max_length=10)
    description: str = Field(..., min_length=1, max_length=200)
    price: int = Field(..., gt=10)
    stock: int
    sold_items: int

class SearchPayload(BaseModel):
    searchBy : str
    value: str
    min: str
    max: str

# Get all books from database
@app.get("/books")
async def index():
    collection = app.mongodb_client.bookStore.books
    result = collection.find()
    res = []
    async for i in result:
        i["_id"] = str(i["_id"])
        res.append(i)
    return JSONResponse(content=res)

# Get Book by id
@app.get("/book/{book_id}")
async def getbookById(book_id:str):
    collection = app.mongodb_client.bookStore.books
    result = await collection.find_one({"_id": ObjectId(book_id)})

    if result:
        result["_id"] = str(result["_id"])
    return result

# Create new book
@app.post("/book")
async def create_user(book: Book):
    print(book)
    collection = app.mongodb_client.bookStore.books
    book_dict = book.dict()
    try:
        result = await collection.insert_one(book_dict)
        if result.inserted_id:
            return {"message": "Book created successfully", "book_id": str(result.inserted_id)}
        else:
            raise HTTPException(status_code=500, detail="Failed to create book")
    except WriteError as w:
        raise HTTPException(status_code=500, detail=f"Saving record failed: {w}")

# update book 
@app.put("/")
async def updateBook(book:Book):
    collection = app.mongodb_client.bookStore.books
    book_dict = book.dict() 
    print(book_dict)
    book_id = book_dict["book_id"]
    book_dict.pop("book_id", None)
    book_oid = ObjectId(book_id)

    try:
        result = await collection.update_one(
            {"_id": book_oid},
            {"$set": book_dict}
        )
        if result.modified_count == 1:
            return {"message": "Book updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Book not found")
    except WriteError as w:
        raise HTTPException(status_code=500, detail=f"Update book failed: {w}")

@app.delete("/books/{book_id}")
async def deleteBook(book_id: str):
    collection = app.mongodb_client.bookStore.books
    result = await collection.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count == 1:
        return {"message": f"Book with ID {book_id} has been deleted."}
    else:
        return {"message": "Book not found."}

# Search functionality using operators
@app.get("/books/search")
async def search(searchPayload: SearchPayload):
    collection = app.mongodb_client.bookStore.books
    match searchPayload.searchBy:
        case "author":
            result = collection.find({ "author": { "$eq": searchPayload.value } })
        case "title":
            result = collection.find({ "title": { "$eq": searchPayload.value } })
        case "price":
            result = collection.find({ "price": { "$lt": int(searchPayload.max), "$gt": int(searchPayload.min) } })
        case _:
            return "Deafult case"
    res = []
    async for i in result:
        i["_id"] = str(i["_id"])
        res.append(i)
    return JSONResponse(content=res)

#Aggregation endpoint that return top 5 authors
@app.get("/books/top5authors")
async def get_top_authors():
    collection = app.mongodb_client.bookStore.books
    pipeline = [
        {"$group": {"_id": "$author", "count": {"$sum": 2}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    result = collection.aggregate(pipeline)
    authors = []
    async for doc in result:
        authors.append(doc['_id'])
    return {"authors": authors}

# Aggregation end point that return top 5 selling books
@app.get("/books/top-selling")
async def get_top_selling_books():
    collection = app.mongodb_client.bookStore.books
    pipeline = [
        {"$group": {"_id": "$title", "total_sold": {"$sum": "$sold_items"}}},
        {"$sort": {"total_sold": 1}},
        {"$limit": 5}
    ]
    result = collection.aggregate(pipeline)
    books = []
    async for doc in result:
        books.append(doc['_id'])
    return {"books": books}

# Aggregation end point that returns total number of books
@app.get("/books/count")
async def get_books_count():
    collection = app.mongodb_client.bookStore.books
    count = await collection.count_documents({})
    return {"count": count}

# Purchase Book by id 
@app.post("/books/purchase/{book_id}")
async def purchaseBook(book_id: str):
    collection = app.mongodb_client.bookStore.books
    query = {"_id": ObjectId(book_id)}
    update = {"$inc": {"sold_items": 1, "stock": -1}}
    try:
        await collection.update_one(query, update)
    except WriteError as e:
        print(f"Purchase failed {e}")
        return False
    return True



   
    



    

