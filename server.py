# from fastapi import FastAPI, WebSocket
# from fastapi.responses import HTMLResponse
# import uvicorn
# import logging
# from datetime import datetime

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = FastAPI()
# messages = []


# html = '''
# <!DOCTYPE html>
# <html>
#     <head>
#         <title>Chat</title>
#     </head>
#     <body>
#         <h1>WebSocket Chat</h1>
#         <form action="" onsubmit="sendMessage(event)">
#             <input type="text" id="messageText" autocomplete="off"/>
#             <button>Send</button>
#         </form>
#         <ul id='messages'>
#         </ul>
#         <script>
#             var ws = new WebSocket("ws://localhost:8000/ws");
#             ws.onmessage = function(event) {
#                 var messages = document.getElementById('messages')
#                 var message = document.createElement('li')
#                 var content = document.createTextNode(event.data)
#                 message.appendChild(content)
#                 messages.appendChild(message)
#             };
#             function sendMessage(event) {
#                 var input = document.getElementById("messageText")
#                 ws.send(input.value)
#                 input.value = ''
#                 event.preventDefault()
#             }
#         </script>
#     </body>
# </html>
# '''
# @app.get("/")
# async def get():
#     return HTMLResponse(html)

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     client_id = id(websocket)
#     logger.info(f"Client connected. ID: {client_id}")
#     try:
#         while True:
#             data = await websocket.receive_text()
#             await websocket.send_text(f"Message received: {data}")
#     except Exception as e:
#         logger.error(f"Error with client {client_id}: {str(e)}")
#     finally:
#         logger.info(f"Client disconnected. ID: {client_id}")

# @app.get("/messages")
# async def get_messages():
#     return {"messages": messages}

# @app.get("/stats")
# async def get_stats():
#     return {
#         "total_messages": len(messages), 
#         "unique_clients": len(set(m["client_id"] for m in messages))
#     }
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)


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

html2 = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://" + window.location.host + "/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""
html3 = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat Room</title>
        <style>
            .chat-container {
                width: 400px;
                border: 1px solid #ccc;
                padding: 10px;
                margin: 0 auto;
            }
            .message {
                margin: 5px 0;
                padding: 5px;
                border-radius: 5px;
                clear: both;
            }
            .own-message {
                background-color: #DCF8C6;
                float: right;
            }
            .other-message {
                background-color: #E8E8E8;
                float: left;
            }
            #username-form {
                margin-bottom: 10px;
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
            var ws;
            var username;

            function setUsername() {
                username = document.getElementById('username').value.trim();
                if (username) {
                    document.getElementById('username-form').style.display = 'none';
                    document.getElementById('chat-area').style.display = 'block';
                    ws = new WebSocket("ws://" + window.location.host + "/ws");
                    
                    ws.onopen = function() {
                        ws.send(JSON.stringify({type: "connect", username: username}));
                    };
                    
                    ws.onmessage = function(event) {
                        var data = JSON.parse(event.data);
                        var messages = document.getElementById('messages');
                        var message = document.createElement('div');
                        message.classList.add('message');
                        message.classList.add(data.username === username ? 'own-message' : 'other-message');
                        message.innerHTML = '<strong>' + data.username + ':</strong> ' + data.message;
                        messages.appendChild(message);
                        messages.scrollTop = messages.scrollHeight;
                    };
                }
            }

            function sendMessage(event) {
                event.preventDefault();
                var input = document.getElementById("messageText");
                var message = input.value;
                if (message) {
                    ws.send(JSON.stringify({type: "message", username: username, message: message}));
                    input.value = '';
                }
            }
        </script>
    </body>
</html>
"""
html1 = """
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
                const usernameInput = document.getElementById('username').value.trim();
                if (usernameInput) {
                    username = usernameInput;
                    document.getElementById('username-form').style.display = 'none';
                    document.getElementById('chat-area').style.display = 'block';
                    
                    ws = new WebSocket("ws://" + window.location.host + "/ws");
                    
                    ws.onopen = function() {
                        ws.send(JSON.stringify({
                            type: "connect",
                            username: username
                        }));
                    };
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        const messages = document.getElementById('messages');
                        const messageDiv = document.createElement('div');
                        messageDiv.classList.add('message');
                        
                        if (data.username === username) {
                            messageDiv.classList.add('own-message');
                        } else {
                            messageDiv.classList.add('other-message');
                        }
                        
                        messageDiv.textContent = `${data.username}: ${data.message}`;
                        messages.appendChild(messageDiv);
                        messages.scrollTop = messages.scrollHeight;
                    };
                }
            }

            function sendMessage(event) {
                event.preventDefault();
                const input = document.getElementById("messageText");
                const message = input.value.trim();
                if (message && username) {
                    ws.send(JSON.stringify({
                        type: "message",
                        username: username,
                        message: message
                    }));
                    input.value = '';
                }
            }
        </script>
    </body>
</html>
"""
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

# @app.websocket("/ws")
# async def websocket_endpoint2(websocket: WebSocket):
#     await manager.connect(websocket)
#     # client_id = id(websocket)
#     username = "Anonymous"
#     try:
#         while True:
#             data = await websocket.receive_text()
#             # manager.add_message(client_id, data)
#             # await manager.broadcast(f"Client {client_id}: {data}")
#             message_data = json.loads(data)
#             if message_data['type'] == 'connect':
#                 username = message_data['username']
#                 logger.info(f"User {username} connected")
#             elif message_data['type'] == 'message':
#                 message = manager.add_message(username, message_data['message'])
#                 await manager.broadcast(message)

#     except Exception as e:
#         logger.error(f"Error with user {username}: {str(e)}")
#     finally:
#         manager.disconnect(websocket)
#         logger.info(f"User {username} disconnected")

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