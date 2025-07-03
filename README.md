# Invoice Extractor

This project is a Flask-based web application for extracting structured data from PDF documents like invoices and bank statements. It uses a large language model (LLM) to parse the text and stores the extracted information in a MongoDB database.

## Project Structure

The codebase is organized into the following directories:

```
.gitignore
/app
  __init__.py
  app.py
  client_request.py
  document_store.py
  fields_to_extract.py
  main.py
  pdf_retrieval_examples.py
  query_examples.py
  query_interface.py
  text_extraction.py
  /static
    /css
    /js
  /templates
    dashboard.html
    index.html
/data
  /final_output
  /pdfs
  /uploads
README.md
requirements.txt
run.py
/tests
```

-   **`app/`**: Contains the core application logic, structured as a Python package.
    -   **`__init__.py`**: Initializes the Flask application.
    -   **`app.py`**: Defines the Flask routes and application setup.
    -   **`main.py`**: Contains the main PDF processing logic.
    -   **`text_extraction.py`**: Handles text extraction from PDF files.
    -   **`fields_to_extract.py`**: Defines the data structures for extracted information.
    -   **`document_store.py`**: Manages interaction with the MongoDB database.
    -   **`client_request.py`**: Handles requests to the LLM.
    -   **`templates/`**: Contains the HTML templates for the web interface.
    -   **`static/`**: Holds static assets like CSS and JavaScript files.
-   **`data/`**: Stores all data files.
    -   **`pdfs/`**: Contains the original PDF documents.
    -   **`uploads/`**:  The default folder for file uploads.
    -   **`final_output/`**: Stores the extracted data in CSV format.
-   **`tests/`**: Contains tests for the application.
-   **`run.py`**: The main entry point to start the Flask application.
-   **`requirements.txt`**: Lists the Python dependencies for the project.
-   **`.gitignore`**: Specifies files and directories to be ignored by Git.
-   **`README.md`**: This file.

## Getting Started

### Prerequisites

-   Python 3.x
-   MongoDB

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd inv_extractor_with_frontend
    ```

2.  **Create and activate a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**

    You will need to configure your MongoDB connection details and any API keys for the LLM service you are using. It is recommended to use a `.env` file for this.

### Running the Application

To start the Flask development server, run the following command:

```bash
python run.py
```

The application will be available at `http://127.0.0.1:5000`.

## How to Use

1.  Navigate to the application in your web browser.
2.  Upload a PDF file using the form.
3.  The application will process the document, extract the relevant information, and display it on the dashboard.
4.  The extracted data will also be saved as a CSV file in the `data/final_output` directory.