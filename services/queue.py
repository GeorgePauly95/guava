from redis import Redis
from rq import Queue
from services.location import handle_message

redis_conn = Redis("localhost", port=6379)
q = Queue(connection=redis_conn)

def dispatch_message(message: dict):
    """
    Dispatches a message to be processed asynchronously.
    """
    q.enqueue(handle_message, message)
