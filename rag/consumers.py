import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .rag_logic import get_rag_response


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        # if not logined => refuse it
        if self.scope["user"].is_anonymous:
            await self.close()
            return
        #  accept the connection
        await self.accept()
        await self.send(text_data=json.dumps({
            "type": "welcome",
            "message": f"welcome! {self.scope['user'].username} your chat is ready :)"
        }))

        # receive message from websocket

    async def receive(self, text_data):
        data = json.loads(text_data)
        query = data.get("message", "").strip()
        if not query:
            return

        # Thinking message
        await self.send(text_data=json.dumps({
            "type": "thinking",
            "message": "Searching on your PDF"
        }))

    # Retrieve response from rag
        full_response = await get_rag_response(self.scope["user"], query)

    # Apply streaming
        for word in full_response.split():
            await self.send(text_data=json.dumps({
                "type": "stream",
                "word": word + " "
            }))
        await asyncio.sleep(0.04)  # writing speed
