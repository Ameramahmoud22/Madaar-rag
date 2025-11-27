import json
from channels.generic.websocket import AsyncWebsocketConsumer

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
        message = data.get('message', '')

        # Echo the received message back to the client
        await self.send(text_data=json.dumps({
            'type': 'reply',
            'message': message
        }))