from copy import deepcopy
from quopri import decodestring
from sqlite3 import connect

from patterns.architectural_system_pattern_unit_of_work import DomainObject

flag = False
# абстрактный пользователь
from patterns.structural_patterns import ParentItem


class User:
    pass


# преподаватель
class Teacher(User):
    pass


# студент
class Student(User, DomainObject):

    def __init__(self, type_, name, email):
        self.name = name
        self.type_ = type_
        self.email = email
        self.courses = []


class UserFactory:
    types = {
        'student': Student,
        'teacher': Teacher
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name, email):
        return cls.types[type_](type_, name, email)


# порождающий паттерн Прототип
class CoursePrototype:
    # прототип курсов обучения

    def clone(self):
        return deepcopy(self)


class Course(CoursePrototype):

    def __init__(self, type_, name, category):
        self.name = name
        self.type_ = type_
        self.category = category
        self.category.courses.append(self)


# интерактивный курс
class PracticeCourse(Course):
    pass


# курс в записи
class TheoryCourse(Course):
    pass


class CourseFactory:
    types = {
        'theory': TheoryCourse,
        'practice': PracticeCourse,
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name, category):
        return cls.types[type_](type_, name, category)


# категория
class Category:
    auto_id = 0

    def __init__(self, name, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.category = category
        self.child_category = []
        self.courses = []

    def course_count(self):
        result = len(self.courses)
        # if self.category:
        #     result += self.category.course_count()
        return result


# основной интерфейс проекта
class Engine:
    def __init__(self):
        self.teachers = []
        self.students = []
        self.courses = []
        self.categories = []

    def default_values(self):
        default_categories_theory = ['Техника безопасности', 'Гайд по снаряжению']
        default_categories_practice = ['Горные лыжи', 'Сноуборд']
        default_courses = ['Новичок', 'Продвинутый', 'Эксперт']
        for category in default_categories_practice:
            new_cat = self.create_category(category)
            self.categories.append(new_cat)
            for course in default_courses:
                new_course = self.create_course('practice', course,
                                                category=self.find_category_by_name(category, self.categories))
                self.courses.append(new_course)
        for category in default_categories_theory:
            new_cat = self.create_category(category)
            self.categories.append(new_cat)
            new_course_th = self.create_course('theory', 'Основы',
                                               category=self.find_category_by_name(category, self.categories))
            self.courses.append(new_course_th)
            new_course_th = self.create_course('theory', 'Бонус',
                                               category=self.find_category_by_name(category, self.categories))
            self.courses.append(new_course_th)

    @staticmethod
    def create_student(name, email):
        return UserFactory.create('student', name, email)

    def get_student(self, name):
        for item in self.students:
            if item.name == name:
                return item
        return None

    def create_category(self, name, category=None):
        if category:
            self.find_category_by_name(category.name, self.categories)
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            # print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    def find_category_by_name(self, cat_name, cat_list):
        for item in cat_list:
            # print('item_name', item.name)
            if item.name == cat_name:
                return item

        raise Exception(f'Нет категории с именем = {cat_name}')

    @staticmethod
    def create_course(type_, name, category):
        return CourseFactory.create(type_, name, category)

    @staticmethod
    def get_course(name, category):
        for item in category.courses:
            if item.name == name:
                return item
        return None

    def get_course_site(self, name):
        for item in self.courses:
            if item.name == name:
                return item
        return None

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = decodestring(val_b)
        return val_decode_str.decode('UTF-8')


# порождающий паттерн Синглтон
class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name):
        self.name = name

    @staticmethod
    def log(text):
        print('log--->', text)


class StudentMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'student'

    def all(self):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, name = item
            student = Student(name)
            student.id = id
            result.append(student)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, name FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()
        if result:
            return Student(*result)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name) VALUES (?)"
        self.cursor.execute(statement, (obj.name,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=? WHERE id=?"

        self.cursor.execute(statement, (obj.name, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


connection = connect('patterns.sqlite')


# архитектурный системный паттерн - Data Mapper
class MapperRegistry:
    mappers = {
        'student': StudentMapper,
        #'category': CategoryMapper
    }

    @staticmethod
    def get_mapper(obj):

        if isinstance(obj, Student):

            return StudentMapper(connection)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](connection)


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')
