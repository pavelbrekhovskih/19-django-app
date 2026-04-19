from datetime import datetime

from django.http import HttpRequest

def set_useragent_on_request_middleware(get_response):
    print("initial call") # Происходит на старте прил-я

    # Эта ф-я принимает request до view ф-и
    def middleware(request: HttpRequest):
        print("Before get_response")
        request.user_agent = request.META["HTTP_USER_AGENT"]
        response = get_response(request) # обработка запроса (во view)
        print("After get_response")
        # Здесь можно обраб-ть ответ и отправить дальше
        # В рез-те мы модифицировали запрос и вернули ответ после обработки view
        return response

    return middleware


class CountRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    # То, что будет вызвано, когда middleware будет обраб-ть запрос
    def __call__(self, request: HttpRequest):
        self.requests_count += 1
        print("requests_count", self.requests_count)
        response = self.get_response(request)
        self.responses_count += 1
        print("responses_count", self.responses_count)

        return response

    # Можно обраб-ть ошибки из view ф-й (также можно вернуть польз-лю ответ с инф-и об ошибке)
    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print("got", self.exceptions_count, "exceptions so far")
