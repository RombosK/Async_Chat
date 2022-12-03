import json
from decor import log
from config import MAX_SIZE_MSG, ENCODING


@log
def get_message(client):
    encoded_response = client.recv(MAX_SIZE_MSG)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


@log
def send_message(sock, message):
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
