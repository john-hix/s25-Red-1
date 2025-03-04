"""Tests for Objects in openapi.py"""
import json

from configuration.openapi import ServerObject



def test_server_object():
    server_object_json = '''{"url": "https://www.example.com", "description":"A description"}'''

    server_object = ServerObject(url="https://www.example.com", description="A description")
    
    server_object2 = ServerObject(**json.loads(server_object_json))

    assert server_object == server_object2