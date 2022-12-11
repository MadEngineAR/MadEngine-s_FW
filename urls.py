import platform
from pprint import pprint

from views import Index, AnotherPage


# front controller
def secret_front(environ, request):
    x = platform.system()
    if platform.system() == 'Darwin':
        pprint(environ)
        print(environ['USER'])
        request['user'] = environ['USER']
    elif platform.system() == 'Windows':
        print(environ['USERNAME'])
        request['user'] = environ['USERNAME']


def other_front(environ, request):
    request['server_name'] = environ['SERVER_NAME']
    request['port'] = environ['SERVER_PORT']


fronts = [secret_front, other_front]

routes = {
    '/': Index(),
    '/index.html/': Index(),
    '/another_page/': AnotherPage(),
}
