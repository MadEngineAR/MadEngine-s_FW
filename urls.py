import platform


from views import Index, CoursesList, CreateCourse, CreateCategory, CategoryList, CopyCourse, Admin, UserCourses


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
    # '/another_page/': AnotherPage(),
    '/courses-list/': CoursesList(),
    '/create-course/': CreateCourse(),
    '/create-category/': CreateCategory(),
    '/admin/': Admin(),
    '/copy-course/': CopyCourse(),
    '/user-courses/': UserCourses(),
}
