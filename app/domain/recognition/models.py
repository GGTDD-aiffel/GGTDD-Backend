from pydantic import BaseModel

class Paraphrase(BaseModel):
    paraphrase_id: str
    recognition_id: str
    paraphrase_content: str
    is_selected_paraphrase: bool
    created_at: str