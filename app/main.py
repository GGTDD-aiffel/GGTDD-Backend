from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def test():
    return {"메세지": "테스트!"}