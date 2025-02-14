from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from agent import Chat_Agent
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import aioredis
import asyncio

redis = aioredis.from_url("redis://127.0.0.1", decode_responses=True)
app = FastAPI(lifespan="lifespan")

RATE_LIMIT = 5
TIME_WINDOW = 20


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.agent = Chat_Agent()

    async def setup(self):
        """Async setup for connections and API initialization"""
        await self.agent.instantiate_api()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://randolfuy.vercel.app/",
        "http://localhost:3000",
        "http://ec2-52-15-254-67.us-east-2.compute.amazonaws.com:8000", 
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles setup and teardown of app lifecycle events"""
    await manager.setup()
    yield
    for connection in manager.active_connections:
        await connection.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def get():
    return "Starting web server"


async def is_rate_limited(client_id: str) -> bool:
    """Ensuring rate limiter using redis by waiting until expiration"""
    key = f"rate_limit:{client_id}"
    try:
        count = await redis.incr(key)

        if count == 1:
            await redis.expire(key, TIME_WINDOW)

        return count > RATE_LIMIT
    except aioredis.exceptions.ConnectionError:
        print("Error connecting to Redis.")
        return False


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    """API for interacting with personal website, allows for agent to interact with users with specified end points
       Ensures rate limited for spam messaging"""
    await manager.connect(websocket)

    try:
        while True:
            if await is_rate_limited(str(client_id)):
                await manager.send_personal_message(
                    "⚠️ Rate limit exceeded. Wait before sending more messages.",
                    websocket,
                )
                await asyncio.sleep(TIME_WINDOW)
                continue

            # Receive message from client
            data = await websocket.receive_text()

            # Process response
            try:
                response = await manager.agent.response(data)
                await manager.send_personal_message(response, websocket)
                print(f"Agent to Client {client_id}: {response}")
            except Exception as e:
                print(f"Error processing message from client {client_id}: {e}")
                await manager.send_personal_message("Sorry, there was an error processing your request.", websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
