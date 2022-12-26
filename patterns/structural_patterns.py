from time import time


from abc import ABCMeta, abstractmethod


class Component(metaclass=ABCMeta):
    @abstractmethod
    def operation(self):
        pass


class ChildItem(Component):
    def __init__(self, name):
        self.name = name

    def operation(self):
        print(self.name)


class ParentItem(Component):
    def __init__(self):
        self._child = []

    def operation(self):
        print('category')
        for child in self._child:
            child.operation()

    def append(self, component):
        self._child.append(component)

    def remove(self, component):
        self._child.remove(component)

    @property
    def child(self):
        return self._child


# структурный паттерн - Декоратор
class AppRoute:
    def __init__(self, routes, url):
        """
        Сохраняем значение переданного параметра
        """
        self.routes = routes
        self.url = url

    def __call__(self, cls):
        """
        Сам декоратор
        """
        self.routes[self.url] = cls()


# структурный паттерн - Декоратор
class Debug:

    def __init__(self, name):
        self.name = name

    def __call__(self, cls):
        """
        сам декоратор
        """

        # это вспомогательная функция будет декорировать каждый отдельный метод класса, см. ниже
        def timeit(method):
            """
            нужен для того, чтобы декоратор класса wrapper обернул в timeit
            каждый метод декорируемого класса
            """

            def timed(*args, **kw):
                ts = time()
                result = method(*args, **kw)
                te = time()
                delta = te - ts

                print(f'debug --> {self.name} выполнялся {delta:2.2f} ms')
                return result

            return timed

        return timeit(cls)

