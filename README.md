# Automation Server Backend

The Automation Server backend works in conjunction with the Automation Server frontend and workers to provide a comprehensive system for running automations. 

## Status

This software is currently in an early alpha stage and is not yet fully documented. 

## License

This project is licensed under the MIT License and comes with no warranty. Use it at your own risk.
## Requirements

- Python 3.7+
- FastAPI
- Uvicorn

## Installation

1. **Clone the repository**:

    ```sh
    git clone https://github.com/odense-rpa/automation-server.git
    cd your-repo-name
    ```

2. **Create a virtual environment**:

    ```sh
    python -m venv .venv
    ```

3. **Activate the virtual environment**:

    - On Windows:

        ```sh
        .venv\Scripts\activate
        ```

    - On macOS/Linux:

        ```sh
        source .venv/bin/activate
        ```

4. **Install the dependencies**:
   
   - Backend:

    ```sh
    pip install -r requirements.txt
    ```

    - Frontend:
   ```sh
    npm install
   ```

## Running the Application

1. **Start the FastAPI server**:

    ```sh
    uvicorn main:app --reload
    ```

    - `main` is the name of the Python file (e.g., `main.py`).
    - `app` is the name of the FastAPI instance.

2. **Access the application**:

    Open your browser and go to `http://127.0.0.1:8000`.

3. **Interactive API documentation**:

    - Swagger UI: `http://127.0.0.1:8000/docs`
    - ReDoc: `http://127.0.0.1:8000/redoc`

## Testing

To run the tests, use:

```sh
pytest
