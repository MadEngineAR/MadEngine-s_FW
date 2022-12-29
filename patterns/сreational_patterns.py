from copy import deepcopy
from quopri import decodestring

from patterns.behavioral_patterns import Subject, EmailNotifier, SmsNotifier


flag = False
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()
# абстрактный пользователь
from patterns.structural_patterns import ParentItem


class User:
    pass


# преподаватель
class Teacher(User):
    pass


# студент
class Student(User):

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


class Course(CoursePrototype, Subject):

    def __init__(self, type_, name, category):
        self.name = name
        self.type_ = type_
        self.category = category
        self.category.courses.append(self)
        self.students = []
        super().__init__()

    def __getitem__(self, item):
        return self.students[item]

    def add_student(self, student: Student):
        self.students.append(student)
        self.notify()



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
                new_course.observers.append(email_notifier)
                new_course.observers.append(sms_notifier)
                self.courses.append(new_course)
        for category in default_categories_theory:
            new_cat = self.create_category(category)
            self.categories.append(new_cat)
            new_course_th = self.create_course('theory', 'Основы',
                                               category=self.find_category_by_name(category, self.categories))
            self.courses.append(new_course_th)
            new_course_th = self.create_course('theory', 'Бонус',
                                               category=self.find_category_by_name(category, self.categories))
            new_course_th.observers.append(email_notifier)
            new_course_th.observers.append(sms_notifier)
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
