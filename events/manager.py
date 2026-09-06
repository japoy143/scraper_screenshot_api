import asyncio

subscribers: dict[str, asyncio.Queue] = {}


def subscribe(subscriber_id: str):
    queue = asyncio.Queue()

    subscribers[subscriber_id] = queue

    return queue


def unsubscribe(subscriber_id: str):
    subscribers.pop(subscriber_id, None)


async def publish(subscriber_id: str, event: dict):
    queue = subscribers.get(subscriber_id)

    if queue:
        await queue.put(event)
