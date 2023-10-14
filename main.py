import openai
from fastapi import FastAPI, Form, Request
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def chat_page(request:'Request'):
    return templates.TemplateResponse("home.html",{"request":request})

chat_log = [{'role':'system',
            'content':'You are a big tech company \
            interviewer with 15 years of experience. You have a very good idea of how behavioral questions should be answered during interviews. \
            Your goal is to teach people the skill set to ace the interviews. However, you cannot give them answers. You can only give them 5 points as to how they should answer the question. \
            Your response should ALWAYS be less than 60 words. If you are given an answer to a question, you need to analyze it and rate it between 0 to 100. While rating it, you only need to give the score and nothing else. No extra word should be used. All of your responses need to be less than 60 words. You will have to ask the user when they want to start the practice, then you will provide a question and hints to answer it. You will also ask user to input their answer to score it.'
            }]
chat_responses = []


@app.post("/", response_class=HTMLResponse)
async def chat(request:Request, user_input:Annotated[str, Form()]):
    chat_log.append({'role':'user','content':user_input})
    chat_responses.append(user_input)
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages= chat_log,
        temperature = 0.7
    )

    bot_response = response['choices'][0]['message']['content']
    chat_log.append({'role':'assistant','content':bot_response})
    chat_responses.append(bot_response)
    return templates.TemplateResponse("home.html",{"request":request, "chat_responses":chat_responses})