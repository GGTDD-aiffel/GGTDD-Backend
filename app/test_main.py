from fastapi.testclient import TestClient
from app.domain.recognition.models import ParaphraseRequest, ParaphraseResponse, RecommendationRequest, RecommendationResponse
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    
    assert response.status_code == 200
    assert response.json() == ["백엔드 서버 실행 중!!"]

# def test_generate_paraphrase():
#     body = ParaphraseRequest(
#         recognition_id="12345",
#         content="안녕하세요. 반갑습니다.",
#         user_context="사용자 컨텍스트 예시"
#     )
    
#     response = client.post(
#         "api/paraphrase",
#         json=body.model_dump(),
#     )

#     print(response.json())

#     assert response.status_code == 200

def test_recommendation():
    body = RecommendationRequest(
        recognition_id="12345",
        user_context="사용자 컨텍스트 예시",
        content="example context"
    )
    
    response = client.post(
        "/api/recommended/context_tags",
        json=body.model_dump(),
    )
    
    print(response.json())
    
    assert response.status_code == 200

def test_temp_actionable_steps():
    body = {
        "recognition_id": "12345",
        "content": "example content"
    }
    
    response = client.post(
        "/api/temp_actionable_steps",
        json=body,
    )
    
    print(response.json())
    
    assert response.status_code == 200