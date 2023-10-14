import openai
from fastapi import FastAPI, Form, Request, WebSocket
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        await websocket.send_text("Assistant: Please type and send 'start' if you are ready to practice")
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_response(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def chat_page(request:'Request'):
    return templates.TemplateResponse("home.html",{"request":request})

chat_log = [{'role':'system',
            'content':'You are a big tech company \
            interviewer with 15 years of experience. You have a very good idea of how behavioral questions should be answered during interviews. \
            Your goal is to teach people the skill set to ace the interviews. However, you cannot give them the answers to any questions. You can only give them 5 points as to how they should answer the question. \
            Your response should ALWAYS be less than 60 words. If you are given an answer to a question, you need to analyze it and rate it between 0 to 100. While rating it, you only need to give the score and nothing else. \
            No extra word should be used. All of your responses need to be less than 60 words. You will have to ask the user when they want to start the practice, then you will provide a question and hints to answer it. \
            You will also ask user to input their answer to score it. Once you score the question, you will provide two line feedback along with the score. You will always start from the question: Tell me about yourself, and then move forward with other questions.\
            Your questions should always be behavioral interview questions with hints to answer it and will not have expertise on any other domain of knowledge.'
            }]
chat_responses = []


@app.post("/", response_class=HTMLResponse)
async def chat(request:Request, user_input:Annotated[str, Form()]):
    chat_log.append({'role':'user','content':user_input})
    chat_responses.append(f'You: {user_input}')
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages= chat_log,
        temperature = 0.7
    )

    bot_response = response['choices'][0]['message']['content']
    chat_log.append({'role':'assistant','content':bot_response})
    chat_responses.append(f'Assistant: {bot_response}')
    return templates.TemplateResponse("home.html",{"request":request, "chat_responses":chat_responses})