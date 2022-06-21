import uvicorn
# from app.main import app
# from app import main

if __name__ == '__main__':
    uvicorn.run("app.main:app", host="0.0.0.0", port=8110, debug=True, log_level='debug')
    # uvicorn.run("app.main:app", port=8003, workers=1, debug=True, log_level="debug", reload=False)
