from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn
import logging
from datetime import datetime
from typing import List
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.messages = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        message_json = json.dumps(message)
        for connection in self.active_connections:
            await connection.send_text(message_json)

    def add_message(self, username: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_data = {
            "username": username,
            "message": message,
            "timestamp": timestamp
        }
        self.messages.append(message_data)
        logger.info(f"Stored message: {message} from client {username}")
        return message_data
app = FastAPI()
manager = ConnectionManager()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat Room</title>
        <style>
            .chat-container {
                width: 400px;
                height: 500px;
                border: 1px solid #ccc;
                padding: 10px;
                margin: 0 auto;
                display: flex;
                flex-direction: column;
            }
            #messages {
                flex-grow: 1;
                overflow-y: auto;
                margin-bottom: 10px;
            }
            .message {
                margin: 5px 0;
                padding: 5px;
                border-radius: 5px;
                max-width: 70%;
                word-wrap: break-word;
            }
            .own-message {
                background-color: #DCF8C6;
                margin-left: auto;
            }
            .other-message {
                background-color: #E8E8E8;
                margin-right: auto;
            }
            #username-form {
                margin-bottom: 10px;
            }
            #message-form {
                display: flex;
            }
            #message-form input {
                flex-grow: 1;
                margin-right: 5px;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div id="username-form">
                <input type="text" id="username" placeholder="Enter your username" />
                <button onclick="setUsername()">Set Username</button>
            </div>
            <div id="chat-area" style="display:none;">
                <div id="messages"></div>
                <form id="message-form" onsubmit="sendMessage(event)">
                    <input type="text" id="messageText" autocomplete="off"/>
                    <button>Send</button>
                </form>
            </div>
        </div>
        <script>
            let ws;
            let username = '';

    function setUsername() {
        username = document.getElementById('username').value.trim();
        if (username) {
            document.getElementById('username-form').style.display = 'none';
            document.getElementById('chat-area').style.display = 'block';
            
            ws = new WebSocket("ws://" + window.location.host + "/ws");
            
            ws.onopen = function() {
                console.log("WebSocket connection opened");
                ws.send(JSON.stringify({type: "connect", username: username}));
            };
            
            ws.onmessage = function(event) {
                console.log("Message received:", event.data);
                var data = JSON.parse(event.data);
                var messages = document.getElementById('messages');
                var messageDiv = document.createElement('div');
                messageDiv.classList.add('message');
                messageDiv.classList.add(data.username === username ? 'own-message' : 'other-message');
                messageDiv.innerHTML = '<strong>' + data.username + ':</strong> ' + data.message;
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
            };
        }
    }

    function sendMessage(event) {
        event.preventDefault();
        var input = document.getElementById("messageText");
        var message = input.value;
        if (message && ws && ws.readyState === WebSocket.OPEN) {
            console.log("Sending message:", {type: "message", username: username, message: message});
            ws.send(JSON.stringify({type: "message", username: username, message: message}));
            input.value = '';
        }
    }        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)
@app.get("/health")
def heath_check():
    return {"status": "healthy"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    username = "Anonymous"
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                logger.info(f"Received raw data: {data}")
                
                if message_data['type'] == 'connect':
                    username = message_data['username']
                    logger.info(f"User {username} connected")
                elif message_data['type'] == 'message':
                    message = manager.add_message(message_data['username'], message_data['message'])
                    await manager.broadcast(message)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
            except KeyError as e:
                logger.error(f"Missing key in message data: {str(e)}")
    except Exception as e:
        logger.error(f"Error with user {username}: {str(e)}")
    finally:
        manager.disconnect(websocket)
        logger.info(f"User {username} disconnected")

@app.get("/messages")
async def get_messages():
    return {"messages": manager.messages}

@app.get("/stats")
async def get_stats():
    return {
        "total_messages": len(manager.messages),
        "active_connections": len(manager.active_connections)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)