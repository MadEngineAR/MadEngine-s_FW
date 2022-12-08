from madengine_framework.templator import render


class Index:
    def __call__(self, request):
        return '200 OK', render('index.html', user=request.get('user', None))


class AnotherPage:
    def __call__(self, request):
        return '200 OK', render('another_page.html', server_name=request.get('server_name', None),
                                port=request.get('port', None))
