import os

import uvicorn
import yaml
from EdgeGPT import Chatbot
from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel


class ReqBody(BaseModel):
    chatText: str = ''
    chatId: int
    chatName: str = 'Master'
    groupId: int = -1
    timestamp: int = -1
    signature: str = ''
    returnVoice: bool = True


with open("config.yaml", "r", encoding="utf-8") as f:
    apicfg = yaml.safe_load(f)

app = FastAPI()
os.environ["COOKIE_FILE"] = "./cookies.json"
bot = Chatbot()


# HelloWorld
@app.get('/')
def read_root():
    return {'HelloWorld': 'BingAI-HTTPAPI'}


@app.post('/{command}')
async def universalHandler(command=None, body: ReqBody = None):
    global bot
    if command is None:
        command = ['chat', 'forgetme']
    # msg = newMsg(body, command)
    prompt: str = body.chatText
    finalMsg: str

    logger.info(f"prompt: {prompt}")
    if command == 'chat':
        resp = await bot.ask(prompt=prompt)
        finalMsg = resp["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"]
    elif command == 'forgetme':
        await bot.reset()
        finalMsg = "已重置对话"
    else:
        finalMsg = "未知命令"
    logger.info(f"finalMsg: {finalMsg}")
    return {'success': True, 'response': finalMsg}


### Run HTTP Server when executed by Python CLI
if __name__ == '__main__':
    uvicorn.run('main:app', host=apicfg['uvicorn_host'], port=apicfg['uvicorn_port'],
                reload=False, log_level=apicfg['uvicorn_loglevel'],
                workers=apicfg['uvicorn_workers'])
