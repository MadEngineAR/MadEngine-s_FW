from quopri import decodestring
from termcolor import colored, cprint
from madengine_framework.FW_requests import PostRequests, GetRequests


class PageNotFound404:
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


class Framework:

    """Класс Framework - основа фреймворка"""

    def __init__(self, routes_obj, fronts_obj):
        self.routes_lst = routes_obj
        self.fronts_lst = fronts_obj

    def __call__(self, environ, start_response):
        # получаем адрес, по которому выполнен переход
        path = environ['PATH_INFO']
        # pprint(environ)
        # добавление закрывающего слеша
        if not path.endswith('/'):
            path = f'{path}/'

        # находим нужный контроллер
        # отработка паттерна page controller
        if path in self.routes_lst:
            view = self.routes_lst[path]
        else:
            view = PageNotFound404()
        request = {}
        # наполняем словарь request элементами
        # этот словарь получат все контроллеры

        # Получаем все данные запроса
        method = environ['REQUEST_METHOD']
        request['method'] = method

        if method == 'POST':
            data = PostRequests().get_request_params(environ)
            request['data'] = Framework.decode_value(data)
            print(f'Нам пришёл post-запрос: {Framework.decode_value(data)}')
            message = Framework.decode_value(data)["comments"].strip(" ")
            from_user = Framework.decode_value(data)["name"]
            from_user_email = Framework.decode_value(data)["email"]
            print(f'Нам пришёл post-запрос: {Framework.decode_value(data)}')
            cprint(f'Cообщение от: {from_user}', 'blue', 'on_grey',
                   ['underline'])
            cprint(f'email: {from_user_email}', 'blue', 'on_grey',
                   ['underline'])
            cprint(f'Текст сообщения: {message}', 'blue', 'on_grey',
                   ['underline'])
            cprint(f'Нам сообщение: {Framework.decode_value(data)}', 'green', 'on_blue')
        if method == 'GET':
            request_params = GetRequests().get_request_params(environ)
            request['request_params'] = Framework.decode_value(request_params)
            if request_params:
                print(f'Нам пришли GET-параметры:'
                      f' {Framework.decode_value(request_params)}')

        # отработка паттерна front controller
        for front in self.fronts_lst:
            front(environ, request)
        # запуск контроллера с передачей объекта request
        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]

    @staticmethod
    def decode_value(data):
        new_data = {}
        for k, v in data.items():
            val = bytes(v.replace('%', '=').replace("+", " "), 'UTF-8')
            val_decode_str = decodestring(val).decode('UTF-8')
            new_data[k] = val_decode_str
        return new_data
