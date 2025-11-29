import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .rag_logic import get_rag_response
import logging
from channels.db import database_sync_to_async
logger = logging.getLogger("django")


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        # only allow authenticated users
        user = self.scope.get("user")
        if not user or getattr(user, "is_anonymous", True):
            await self.close()
            return
        # accept the connection
        await self.accept()
        await self.send(text_data=json.dumps({
            "type": "welcome",
            "message": f"Welcome {user.username}! Chat is ready."
        }))

        # receive message from websocket

    async def receive(self, text_data=None, bytes_data=None):
        # parse incoming JSON
        try:
            data = json.loads(text_data or "{}")
        except Exception:
            await self.send(text_data=json.dumps({"type": "error", "message": "invalid json"}))
            return

        query = (data.get("message") or data.get("query") or "").strip()
        if not query:
            await self.send(text_data=json.dumps({"type": "error", "message": "empty query"}))
            return

        # Thinking message
        await self.send(text_data=json.dumps({
            "type": "thinking",
            "message": "Searching on your PDF"
        }))

   # call simple rag helper (runs blocking ops safely)
        try:
            answer = await get_rag_response(self.scope["user"], query)
        except Exception as e:
            logger.exception("RAG helper failed")
            await self.send(text_data=json.dumps({"type": "error", "message": "internal error"}))
            return

    # Apply streaming word-by-word
        for w in str(answer).split():
            await self.send(text_data=json.dumps({"type": "stream", "word": w + " "}))
            await asyncio.sleep(0.03)

    # send done message
        await self.send(text_data=json.dumps({
            "type": "done"
        }))

    @database_sync_to_async
    def disconnect(self, code):
        logger.info("WebSocket disconnected: %s", code)
