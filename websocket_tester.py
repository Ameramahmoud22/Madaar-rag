import asyncio
import json
import websockets
import sys


async def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python websocket_tester.py <ab17a66d6d83ca72abe1461d830b99c57e8681f3>")
        return

    token = sys.argv[1]
    uri = f"ws://127.0.0.1:8000/ws/chat/?token={token}"

    try:
        async with websockets.connect(uri) as ws:
            print("--- Connected to WebSocket ---")

            # First message should be welcome
            welcome_msg = await ws.recv()
            print("Received:", welcome_msg)

            # Send a query
            query = {"query": "Tell me about the Django framework."}
            await ws.send(json.dumps(query))
            print(f"--- Sent query: {query['query']} ---")

            # Receive messages until 'done' type is received
            while True:
                msg_str = await ws.recv()
                msg = json.loads(msg_str)
                print("Received:", msg)
                if msg.get("type") == "done":
                    print("--- 'done' message received. Closing connection. ---")
                    break

    except websockets.exceptions.ConnectionClosed as e:
        print(f"--- Connection closed unexpectedly: {e} ---")
        print("--- Please check if your server is running and the token is valid. ---")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Make sure to install websockets: pip install websockets
    asyncio.run(main())
