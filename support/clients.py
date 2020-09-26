"""Возаимодействия с клиентами"""
import json
from pathlib import Path

clientBase = Path(__file__).parents[1] / "database" / "clientBase.json"
clientsRequests = Path(__file__).parents[1] / "database" / "clientsRequests.json"


def add_client(info):
    with open(clientBase, 'r') as f:
        list_of_clients = json.loads(f.read())
    list_of_clients.append(info)
    with open(clientBase, 'w') as f:
        f.write(json.dumps(list_of_clients))


def add_client_req(info):
    with open(clientsRequests, 'r') as f:
        list_of_requests = json.loads(f.read())
    list_of_requests.append(info)
    with open(clientsRequests, 'w') as f:
        f.write(json.dumps(list_of_requests))
