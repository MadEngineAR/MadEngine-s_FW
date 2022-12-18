import datetime
from madengine_framework.templator import render
from patterns.сreational_patterns import Engine, Logger

site = Engine()
# Заполняем сайт категориями и курсами по умолчанию
site.default_values()

logger = Logger('main')


# контроллер - главная страница
class Index:
    def __call__(self, request):
        return '200 OK', render('index.html', user=request.get('user', None), categories=site.categories,
                                year=datetime.date.today().year)


# class AnotherPage:
#     def __call__(self, request):
#         content = {'server_name': request.get('server_name', None),
#                    'port': request.get('port', None)
#                    }
#         return '200 OK', render('another_page.html', content=content)


# контроллер "О проекте"
class About:
    def __call__(self, request):
        return '200 OK', render('about.html')


# контроллер - Администрирование
class Admin:
    def __call__(self, request):
        return '200 OK', render('admin.html', objects_list=site.categories)


# контроллер 404
class NotFound404:
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


# контроллер - список курсов
class CoursesList:
    def __call__(self, request):
        logger.log('Список курсов')
        try:
            category = site.find_category_by_id(
                int(request['request_params']['id']))
            return '200 OK', render('course_list.html',
                                    objects_list=category.courses,
                                    name=category.name, id=category.id)
        except KeyError:
            return '200 OK', 'No courses have been added yet'


# контроллер - создать курс
class CreateCourse:
    category_id = -1

    def __call__(self, request):
        if request['method'] == 'POST':
            # метод пост
            data = request['data']
            name = data['name']
            type_ = data['type_']
            name = site.decode_value(name)
            type_ = site.decode_value(type_)
            category = None
            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))
                course = site.create_course(type_, name, category)
                site.courses.append(course)
            return '200 OK', render('course_list.html',
                                    objects_list=category.courses,
                                    name=category.name,
                                    id=category.id)

        else:
            try:
                self.category_id = int(request['request_params']['id'])
                category = site.find_category_by_id(int(self.category_id))

                return '200 OK', render('create_course.html',
                                        name=category.name,
                                        id=category.id)
            except KeyError:
                return '200 OK', 'No categories have been added yet'


# контроллер - создать категорию
class CreateCategory:
    def __call__(self, request):

        if request['method'] == 'POST':
            # метод пост

            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category_id = data.get('category_id')

            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)
            site.categories.append(new_category)

            return '200 OK', render('index.html',
                                    categories=site.categories,
                                    year=datetime.date.today().year)
        else:
            categories = site.categories
            return '200 OK', render('create_category.html',
                                    categories=categories)


# контроллер - список категорий
class CategoryList:
    def __call__(self, request):
        logger.log('Список категорий')
        return '200 OK', render('category_list.html',
                                objects_list=site.categories)


# контроллер - копировать курс
class CopyCourse:
    def __call__(self, request):
        request_params = request['request_params']
        print(request_params)

        try:
            name = request_params['name']
            old_course = site.get_course(name)
            category_id = old_course.category.id
            # print(category_id)
            category = site.find_category_by_id(int(category_id))
            if old_course:
                new_name = f'copy_{name}'
                new_course = old_course.clone()
                new_course.name = new_name
                site.courses.append(new_course)
                category.courses.append(new_course)
                # print(new_course.category)
                # for course in category.courses:
                #     print(course.name)
                return '200 OK', render('course_list.html',
                                        objects_list=category.courses,
                                        name=new_course.category.name)
        except KeyError:
            return '200 OK', 'No courses have been added yet'
