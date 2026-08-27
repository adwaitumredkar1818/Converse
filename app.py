import uvicorn
from api import app

if __name__ == "__main__":
    print("Starting Converse AI UI Backend...")
    uvicorn.run(app, host="0.0.0.0", port=8501)
