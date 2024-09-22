import json
from collections import OrderedDict


class Response:
    def __init__(self, code, message, data):
        self.code = code
        self.message = message
        self.data = data

    def __response_status(self):
        return "success" if self.code == 200 else "error"

    def resp(self):
        resp_dict = {
            "meta": {
                "status":   self.__response_status(),
                "message":  self.message,
            },
            "data": self.data,
        }
        return json.dumps(OrderedDict(resp_dict)), self.code

    @staticmethod
    def success(data):
        return Response(200, "", data)

    @staticmethod
    def error(code, message):
        return Response(code, message, None)

    @staticmethod
    def bad_request(message):
        return Response.error(400, message)

    @staticmethod
    def not_found(message):
        return Response.error(404, message)

    @staticmethod
    def internal_server_error(message):
        return Response.error(500, message)
