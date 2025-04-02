import firebase_admin
from firebase_admin import credentials

from fastapi import FastAPI

# 인증 초기화 (환경 변수 사용)
if not firebase_admin._apps:
    firebase_admin.initialize_app(credentials.Certificate("/secrets/serviceAccountKey.json"))
    
from app.interfaces.controllers import actionable_step_controller, inbox_controller, recognition_controller, user_controller

app = FastAPI()

app.include_router(inbox_controller.router)
app.include_router(user_controller.router)
app.include_router(recognition_controller.router)
app.include_router(actionable_step_controller.router)

@app.get("/")
def read_root():
    return {"백엔드 서버 실행 중!!"}

# 모든 응답에 UTF-8 인코딩 명시
@app.middleware("http")
async def add_utf8_content_type(request, call_next):
    response = await call_next(request)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

