from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from starlette import status
from starlette.responses import JSONResponse

from app.exceptions import GeneralException
from app.responses import get_resp_status_dict
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


def get_validation_error_text(exc: ValidationError | RequestValidationError, title: str):
    def get_query_param_input(error):
        return '' if error['type'] == 'missing' else f" : Input '{error['input']}'"

    # print(f"get_validation_error_text errors = {exc.errors()}")
    return f"{title}: " + \
        '; '.join(
            [
                f"{'.'.join([str(loc) for loc in x['loc']])} : {x['msg']}{get_query_param_input(x)}"
                for x in exc.errors()
            ]
        )


def get_request_validation_error_text(exc: RequestValidationError):
    return get_validation_error_text(exc, 'Ошибка валидации http-запроса')


def get_response_validation_error_text(exc: ValidationError):
    return get_validation_error_text(exc, 'Ошибка валидации http-ответа')


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    msg = get_request_validation_error_text(exc)
    GeneralException(status.HTTP_400_BAD_REQUEST, msg)
    return JSONResponse(
        content=get_resp_status_dict(status.HTTP_400_BAD_REQUEST, msg),
        status_code=status.HTTP_400_BAD_REQUEST
    )
