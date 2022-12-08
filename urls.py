from datetime import date
from views import Index, AnotherPage


# front controller
def secret_front(environ, request):
    print(environ['USER'])
    request['user'] = environ['USER']


def other_front(environ, request):
    request['server_name'] = environ['SERVER_NAME']
    request['port'] = environ['SERVER_PORT']


fronts = [secret_front, other_front]

routes = {
    '/': Index(),
    '/index.html/': Index(),
    '/another_page.html/': AnotherPage(),
}
