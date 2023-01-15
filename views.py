import datetime
from madengine_framework.templator import render
from patterns.structural_patterns import AppRoute, Debug
from patterns.сreational_patterns import Engine, Logger, MapperRegistry
from patterns.architectural_system_pattern_unit_of_work import UnitOfWork

site = Engine()
# Заполняем сайт категориями и курсами по умолчанию
site.default_values()

logger = Logger('main')

routes = {}

UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)


@AppRoute(routes=routes, url='/')  # контроллер - главная страница
class Index:
    @Debug(name='Index')
    def __call__(self, request):
        return '200 OK', render('index.html', user=request.get('user', None), categories=site.categories,
                                year=datetime.date.today().year)


# контроллер "О проекте"
# class About:
#     def __call__(self, request):
#         return '200 OK', render('about.html')


# контроллер - Администрирование
@AppRoute(routes=routes, url='/admin/')
class Admin:
    @Debug(name='Admin')
    def __call__(self, request):
        return '200 OK', render('admin.html', objects_list=site.categories)


# контроллер 404
class NotFound404:
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


# контроллер - список курсов
@AppRoute(routes=routes, url='/courses-list/')
class CoursesList:
    @Debug(name='courses-list')
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


# контроллер - список курсов
@AppRoute(routes=routes, url='/user-courses/')
class UserCourses:
    @Debug(name='user-courses')
    def __call__(self, request):
        logger.log('Список курсов пользователя')
        if request['method'] == 'POST':
            try:
                name = request['data']['name']
                email = request['data']['email']
                name = site.decode_value(name)
                email = site.decode_value(email)
                if site.get_student(name):
                    student = site.get_student(name)
                else:
                    student = site.create_student(name, email)
                    site.students.append(student)
                    student.mark_new()
                    UnitOfWork.get_current().commit()
                course_param = request['data']['course'].split('-')
                # print(course_param)
                course_name = course_param[1].strip(' ')
                course_cat_name = course_param[0].strip(' ')
                course_cat = site.find_category_by_name(course_cat_name, site.categories)
                course = site.get_course(course_name, course_cat)
                if course not in student.courses:
                    student.courses.append(course)

                    return '200 OK', render('students_list.html',
                                            objects_list=site.students)
                return '200 OK', render('students_list.html',
                                        objects_list=site.students, message='Вы уже записаны на этот курс')
            except KeyError:
                return '200 OK', 'No courses have been added yet'
        else:
            return '200 OK', render('students_list.html',
                                    objects_list=site.students)


# контроллер - создать курс
@AppRoute(routes=routes, url='/create-course/')
class CreateCourse:
    category_id = -1

    @Debug(name='create-course')
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
@AppRoute(routes=routes, url='/create-category/')
class CreateCategory:
    @Debug(name='create-category')
    def __call__(self, request):
        print(request)
        if request['method'] == 'POST':
            # метод пост

            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category_name = data.get('category')

            if category_name != 'None':
                category = site.find_category_by_name(category_name, site.categories)
                new_child_category = site.create_category(name, category)
                category.child_category.append(new_child_category)
                site.categories.append(new_child_category)
            else:
                category = None
                # print(category)
                new_category = site.create_category(name, category)
                site.categories.append(new_category)
            for item in site.categories:
                if item.category:
                    print(f'{item.name} - {item.category.name}')
                else:
                    print(f'{item.name} - {item.category}')

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
@AppRoute(routes=routes, url='/copy-course/')
class CopyCourse:
    @Debug(name='copy-course')
    def __call__(self, request):
        request_params = request['request_params']
        print(request_params)

        try:
            name = request_params['name']
            name = site.decode_value(name)
            category = site.find_category_by_id(int(request_params['id']))
            old_course = site.get_course(name, category)
            if old_course:
                new_name = f'copy_{name}'
                new_course = old_course.clone()
                new_course.name = new_name
                site.courses.append(new_course)
                category.courses.append(new_course)
                return '200 OK', render('course_list.html',
                                        objects_list=category.courses,
                                        name=new_course.category.name, id=category.id)
        except KeyError:
            return '200 OK', 'No courses have been added yet'
