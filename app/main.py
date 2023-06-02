from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from app.routers.routers import router
from app.db.datasources import init as dsinit
from app.logapi import init as loginit


app = FastAPI(debug=True,
              title='Reporter API',
              version='1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

loginit()
dsinit()
