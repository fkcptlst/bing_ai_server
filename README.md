# Bing AI Api Server

## Introduction

A simple api server for Bing AI Api. Implemented using fastapi. Reverse engineering based on [
EdgeGPT](https://github.com/acheong08/EdgeGPT).

## Deployment

1. clone this repo
2. add `cookies.json` to the current server directory. Format is described in [EdgeGPT](https://github.com/acheong08/EdgeGPT).
3. install dependencies: `pip install -r requirements.txt`
4. run the server: `python main.py`

## Usage

### `GET /`

**Functionality**: test connection

### `GET /style/{style}`

**Functionality**: change style, `style` can be 'creative', 'balanced', 'precise'

### `POST /{command}`

**Functionality**: chat or reset the conversation.

`command` can be 'chat', 'forgetme'

#### `POST /chat`

**Functionality**: chat with the bot. 

**Format**: The request body format is described using pydantic. only `chatText` and `chatId` are required, others are for compatibility with OpenaiBot.

```python
class ReqBody(BaseModel):
    chatText: str = ''
    chatId: int
    chatName: str = 'Master'
    groupId: int = -1
    timestamp: int = -1
    signature: str = ''
    returnVoice: bool = False
```

#### `POST /forgetme`

**Functionality**: clear the conversation history.

**Format**: body is same as `POST /chat` with useless fields.