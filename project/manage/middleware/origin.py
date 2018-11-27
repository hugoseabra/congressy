import socket


class OriginMiddleware(object):

    def process_response(self, request, response):
        response['X-Origin-Server'] = socket.gethostname()
        return response
