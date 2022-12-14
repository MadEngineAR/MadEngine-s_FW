import platform


from views import Index, AnotherPage


# front controller
def secret_front(environ, request):
    if platform.system() == 'Darwin':
        request['user'] = environ['USER']
    elif platform.system() == 'Windows':
        request['user'] = environ['USERNAME']


def other_front(environ, request):
    request['server_name'] = environ['SERVER_NAME']
    request['port'] = environ['SERVER_PORT']


fronts = [secret_front, other_front]

routes = {
    '/': Index(),
    '/another_page/': AnotherPage(),
}
