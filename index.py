#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json
from activity import Activity
from configparser import ConfigParser
from PIL import Image

parser = ConfigParser()
parser.read(".env")
v_token = parser.get('strava_dev_credentials', 'VERIFY_TOKEN')

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = self.path

        query = urlparse(self.path).query

        if len(query.split("&")) > 1:
            query_components = dict(qc.split("=") for qc in query.split("&"))

            if parsed_path.path == "/webhook":
                VERIFY_TOKEN = v_token
                mode = query_components['hub.mode'];
                token = query_components['hub.verify_token'];
                challenge = query_components['hub.challenge'];
                print("here", challenge)
                if mode and token:
                    if mode == "subscribe" and token == VERIFY_TOKEN:
                        print("WEBHOOK_VERIFIED")
                        print("RETURNING", { "hub.challenge": challenge})
                        print(json.dumps({
                            "hub.challenge": challenge
                        }))
                        print(json.dumps({
                            "hub.challenge": challenge
                        }).encode())
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            "hub.challenge": challenge
                        }).encode())
                        return
                    else:
                        self.send_response(403)


        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({
            'method': self.command,
            'path': self.path,
            'real_path': parsed_path.query,
            'query': parsed_path.query,
            'request_version': self.request_version,
            'protocol_version': self.protocol_version
        }).encode())
        return

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        parsed_path = urlparse(self.path)

        path = self.path

        if parsed_path.path == "/webhook":
            print("webhook event received!", post_data);
            self.send_response(200)
            self.end_headers()
            self.wfile.write(("EVENT_RECEIVED").encode())

            if data["aspect_type"] == "update" and data["object_type"] == "activity":
                activity_obj = Activity(data["object_id"])
                activity_obj.fetch_data()
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({
            'method': self.command,
            'path': self.path,
            'real_path': parsed_path.query,
            'query': parsed_path.query,
            'request_version': self.request_version,
            'protocol_version': self.protocol_version,
            'body': data
        }).encode())
        return

if __name__ == '__main__':
    import sys
    server = HTTPServer(('localhost', 8080), RequestHandler)
    print('Starting server at http://localhost:8080')
    server.serve_forever()

