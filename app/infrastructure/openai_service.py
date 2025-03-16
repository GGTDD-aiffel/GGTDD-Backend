import openai

class OpenAIService:
    def __init__(self):
        openai.api_key = 'your-openai-api-key'

    def generate_paraphrase(self, content: str) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Rephrase this: {content}"}]
        )
        return response["choices"][0]["message"]["content"]
    
    def generate_context_tags(self, content: str) -> dict:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Generate context and tags for: {content}"}]
        )
        return eval(response["choices"][0]["message"]["content"])
    
    def generate_temp_actionable_steps(self, content: str) -> list[str]:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Generate actionable steps for: {content}"}]
        )
        return response["choices"][0]["message"]["content"].split('\n')
    

    def recommend_actionable_steps(self, steps: list[str]) -> list[str]:
        prompt = f"Prioritize these actionable steps for today: {', '.join(steps)}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"].split('\n')

    def recommend_current_actionable_step(self, steps: list[str], current_time: str) -> str:
        prompt = f"Given the current time {current_time}, recommend the most suitable actionable step from: {', '.join(steps)}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]