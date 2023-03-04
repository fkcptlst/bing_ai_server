import asyncio
import os
import time

import uvicorn
import yaml
from EdgeGPT import Chatbot, ConversationStyle
from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel
from websockets.exceptions import ConnectionClosedError


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

semaphore = asyncio.Semaphore(1)  # concurrency limit is 1
app = FastAPI()
os.environ["COOKIE_FILE"] = "./cookies.json"
bot = Chatbot()
conv_style = None


# HelloWorld
@app.get('/')
def read_root():
    return {'HelloWorld': 'BingAI-HTTPAPI'}


@app.post('/{command}')
# @retry.retry(tries=3, delay=3)
async def universalHandler(command=None, body: ReqBody = None):
    global bot
    global semaphore
    global conv_style
    async with semaphore:
        if command is None:
            command = ['chat', 'forgetme']
        # msg = newMsg(body, command)
        prompt: str = body.chatText
        finalMsg: str

        logger.info(f"prompt: {prompt}")
        if command == 'chat':
            try:
                resp = await bot.ask(prompt=prompt, conversation_style=conv_style)
            except ConnectionResetError:
                logger.warning("ConnectionResetError, retrying...")
                time.sleep(2)
                resp = await bot.ask(prompt=prompt, conversation_style=conv_style)
            except ConnectionClosedError:
                logger.warning("ConnectionClosedError, retrying...")
                time.sleep(2)
                resp = await bot.ask(prompt=prompt, conversation_style=conv_style)
            try:
                # finalMsg = resp["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"]
                # resp_text: str = resp["item"]["messages"][-1]["text"]
                # resp_text: str = resp["item"]["messages"][-1]["spokenText"]
                # get spokenText or text
                resp_text: str = resp["item"]["messages"][-1].get("text", None)
                author: str = resp["item"]["messages"][-1].get("author", None)
                # if resp_text is None:
                #     resp_text: str = resp["item"]["messages"][-1]["spokenText"]
                try:
                    resp_choices: set[str] = [c["text"] for c in resp["item"]["messages"][-1]["suggestedResponses"]]
                    logger.debug(f"resp_choices: {resp_choices}")
                except KeyError:
                    resp_choices = None
                    pass
                logger.debug(f"resp_text: {resp_text}")
                if author == 'user':
                    finalMsg = "Bing 拒绝回答了。"
                elif resp_choices is None:
                    finalMsg = resp_text
                else:
                    finalMsg = resp_text + "\n\n推荐回复：\n"
                    for i, choice in enumerate(resp_choices):
                        finalMsg += f"{i + 1}. {choice}\n"
            except KeyError as e:
                logger.error(f"KeyError: {e}; resp:{resp}")
                finalMsg = "KeyError"  # Too fast
        elif command == 'forgetme':
            try:
                await bot.reset()
            except Exception as e:
                logger.error(f"Exception: {e}")
                # restart bot
                bot = Chatbot()
            finalMsg = "已重置对话"  # Reset conversation
        else:
            finalMsg = "未知命令"  # Unknown command
        logger.info(f"finalMsg: {finalMsg}")
        return {'success': True, 'response': finalMsg}


@app.get('/style/{style}')
async def styleHandler(style: str = None):
    global conv_style
    # style should be creative,balanced,precise
    if style in ['creative', 'balanced', 'precise']:
        conv_style = ConversationStyle[style]
        return {'success': True, 'response': f"已设置对话风格为:{style}"}
    else:
        return {'success': False, 'response': f"未知风格:{style}"}


### Run HTTP Server when executed by Python CLI
if __name__ == '__main__':
    uvicorn.run('main:app', host=apicfg['uvicorn_host'], port=apicfg['uvicorn_port'],
                reload=False, log_level=apicfg['uvicorn_loglevel'],
                workers=apicfg['uvicorn_workers'])
