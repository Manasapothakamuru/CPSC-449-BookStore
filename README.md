# Group Information

* Naveen Kumar Golla <naveeng@csu.fullerton.edu> 885185843
* Lakshmi Manasa Pothakamuru  <Manasapothakamuru@csu.fullerton.edu> 885214536
* Sai Chand Meda <medasai@csu.fullerton.edu> 885237370

# FastAPI Project Setup

**book Store**: In this project, we created an online bookstore API that allows users to view, search,
and purchase books. The API will be built using FastAPI and the book data will be stored
in MongoDB.  

## Setup

1. Clone this repository to your local machine:

```bash
git clone https://github.com/Manasapothakamuru/CPSC-449-BookStore.git
```

2. Create a virtual environment for the project:

```bash
python3 -m venv venv
```

3. Activate the virtual environment:

```bash
venv/bin/activate
```

4. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Application

To start the fastAPI application, run the following command:

```bash
 uvicorn main:app --reload
```

This will start the application on `http://127.0.0.1:8000/`.


## Features

- GET /books: Retrieves a list of all books in the store
- GET /books/{book_id}: Retrieves a specific book by ID
- POST /books: Adds a new book to the store
- PUT /books/{book_id}: Updates an existing book by ID
- DELETE /books/{book_id}: Deletes a book from the store by ID
- GET /search?title={}&author={}&min_price={}&max_price={}: Searches for books
by title, author, and price range

## Screenshots

![App Screenshot]()

