# FastAPI Project for Product and Ingredient Management

This FastAPI application manages product composition, raw materials, and ingredient data with MySQL as the database. It supports CRUD operations and the generation of various regulatory documents. Additionally, it utilizes MS Graph API for email notifications.

## Features

- **Product and Ingredient Management:** Create, read, update, and delete product and ingredient data in a MySQL database.
- **Document Generation:** Generate PDF documents based on various templates.
- **Data Validation:** Ensures product and ingredient data integrity via database constraints.

## Requirements

- Python 3.8+
- MySQL database
- FastAPI
- SQLAlchemy
- Asynchronous execution with `asyncio`
- `python-multipart` for handling file uploads (optional)
- MS Graph API for email notifications (if implemented)
- PDF generation libraries for creating the documents

## Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/tcw-akshay-soner/Elixir-Backend.git
    cd Elixir-Backend
    ```

2. **Install dependencies:**

    Create a virtual environment and install the required Python packages:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3. **Configure MySQL database:**

    - Set up the MySQL database and create the necessary tables (this is handled in the `lifespan` context).
    - Modify the `src/engine/pharma_db.py` file to include your database credentials (if not already done).

4. **Set up environment variables:**

5. **Run the application:**

    Start the FastAPI server:

    ```bash
    uvicorn main:app --reload
    ```

    This will run the app at `http://127.0.0.1:8000`.

## Endpoints

### 1. `/elixir/product_composition`
- **Method:** `PUT`
- **Description:** Insert product composition data into the database.
- **Request body:** JSON
    ```json
    {
        "product_id": "123",
        "ingredients": [
            {
                "ing_item_code": "ING001",
                "ing_name": "Ingredient Name",
                "per_composition": 50
            }
        ],
        "created_at": "2025-01-29"
    }
    ```
- **Response:** `{"message": "Product Composition data inserted successfully!"}`

### 2. `/elixir/raw_material`
- **Method:** `PUT`
- **Description:** Insert raw material and declaration data into the database.
- **Request body:** JSON
    ```json
    {
        "ing_item_code": "ING001",
        "ing_name": "Ingredient Name",
        "vendor": "Vendor Name",
        "rm_code": "RM001",
        "cas_num": "123-45-6",
        "ec_num": "789-12",
        "ing_type": "Type",
        "source_type": "Natural",
        "source": "Source Name",
        "country_origin": "USA",
        "created_at": "2025-01-29"
    }
    ```
- **Response:** `{"message": "Raw Material data inserted successfully!"}`

### 3. `/elixir/fetch_product`
- **Method:** `GET`
- **Description:** Retrieve all product records.
- **Response:** 
    ```json
    {
        "data": [
            {"product_id": "123", "product_name": "Product A", "created_at": "2025-01-29"}
        ]
    }
    ```

### 4. `/elixir/fetch_items/{product_id}`
- **Method:** `GET`
- **Description:** Fetch all items (ingredients) related to a specific product.
- **Response:** 
    ```json
    {
        "data": [
            {"ing_name": "Ingredient A", "per_composition": 50}
        ]
    }
    ```

### 5. `/elixir/generate_document`
- **Method:** `POST`
- **Description:** Generate a document based on a specific template.
- **Request body:** JSON
    ```json
    {
        "template_name": "gras",
        "company_name": "Company ABC",
        "product_id": "123"
    }
    ```
- **Response:** A PDF document file will be returned with the correct template.

### 6. `/elixir/ingredient`
- **Method:** `GET`
- **Description:** Retrieve all distinct ingredients.
- **Response:**
    ```json
    {
        "data": [
            {"ing_name": "Ingredient A", "ing_item_code": "ING001"},
            {"ing_name": "Ingredient B", "ing_item_code": "ING002"}
        ]
    }
    ```


## Logging

Logging is enabled and will log detailed information about any errors or important events. Ensure the logging configuration is set up in `main.py`.

## Notes

- Ensure the MySQL database is running and accessible.
- The project supports asynchronous operations, so actions that involve database queries are handled without blocking the main thread.
- For generating documents, ensure that the template functions are defined and available in the `template_file` folder.
