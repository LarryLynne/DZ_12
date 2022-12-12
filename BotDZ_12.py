import os
from collections import UserDict
import re
from datetime import datetime, timedelta
import pickle


messages = {
    -1: '- Done',
    0: '- Unknown command',
    1: '- More arguments needed',
    2: '- Too many arguments',
    3: '- Incorrect phone',
    4: '- Phone not found',
    5: '- Good bye!',
    6: '- How can I help you?',
    7: '- There is no any records in phonebook',
    8: '- Incorrect phone number',
    9: '- Invalid date of birth',
    10: '- User already exists',
    11: '- User not found',
    12: '- Address book not saved',
    13: '- Cannot load address book',
    14: '- Users not found'
}


def error_processor(func):
    def inner(promt: str):
        try:
            return func(promt)
        except ValueError as exception:
            return exception.args[0]
        except StopIteration as exception:
            pass
        except KeyError as exception:
            return exception.args[0]
    return inner


class Field:
    def __init__(self, value):
        self._value = None
        self.value = value
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        self._value = value


class Name(Field):
    def __str__(self) -> str:
        return str(self._value)


class Phone(Field):
    @Field.value.setter
    def value(self, value):
        if value:
            ph = re.findall(r"[+][\d]{3}[(][\d]{2}[)][\d]{3}[-][\[\d]{2}[-][\d]{2}]?", value)
            if ph:
                self._value = (str(value))
            else:
                raise ValueError(messages.get(8))
        else:
            self._value = (str(value))


    def __str__(self) -> str:
        return str(self._value)


class BirthDay(Field):
    @Field.value.setter
    def value(self, value):
        if value:
            db = re.findall(r"[\d]{4}[-][\d]{2}[-][\d]{2}", value)
            if db:
                db_parts = str(db[0]).split("-")
                if int(db_parts[0])>=1930 and int(db_parts[1])<=12 and int(db_parts[2])<=31:
                    self._value = (str(value))
                else:
                    raise ValueError(messages.get(9))
            else:
                raise ValueError(messages.get(9))
        else:
            self._value = (str(value))


    def __str__(self) -> str:
        return str(self._value)


class Record:
    def __init__(self, user_name: str, user_phones: tuple = (), user_birthday: str = '') -> None:
        self.name: Name = Name(user_name)
        self.phones: list[Phone] = list()
        for uph in user_phones:
            self.add_phone(uph)

        self.birthday: BirthDay = BirthDay(user_birthday)

    def __str__(self) -> str:
        res = str(self.name) + ", phones: "
        for ph in self.phones:
            res += str(ph) + ", "
        res += "birthday: " + str(self.birthday)
        return res
    
    def add_phone(self, user_phone: str):
        self.phones.append(Phone(user_phone))

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now().date()
            db = datetime(year = datetime.now().year, month = int(str(self.birthday).split("-")[1]), day = int(str(self.birthday).split("-")[2]))
            db = db.date()
            if db < today:
                db += timedelta(days= 365)
            return (db-today).days
        else:
            return 'ХЗ'


class AddressBook(UserDict):
    pos = 0
    count_of_items_for_iterator = 3
    
    def __next__(self):
        if self.pos < len(self.keys()):
            res = ""
            i = self.pos
            k = list(self.data.keys())
            while i < self.pos + self.count_of_items_for_iterator and i < len(k):
                res += str(self.data.get(k[i])) + '\n'
                i += 1
            self.pos = i
            return res
        raise StopIteration    

    def add_record(self, record: Record):
        if self.get(str(record.name)):
            raise KeyError(messages.get(10))
        else:
            self.update({str(record.name): record})

    def show_all(self):
        res = ''
        keys = self.keys()
        if keys:
            for rec in keys:
                res += str(self.get(rec)) + '\n'
            return res
        else:
            raise ValueError(messages.get(7))

    def update_record(self, record: Record):
        if self.get(str(record.name)):
           self.update({str(record.name): record})
        else:
             raise KeyError(messages.get(11))

    def find_user(self, name:str) -> Record:
        res = self.get(name)
        if res:
            return res
        else:
            raise KeyError(messages.get(11))

    def add_phone(self, user: str, phone: str):
        usr = self.find_user(user)
        if usr:
            usr.add_phone(phone)
        else:
            raise KeyError(messages.get(11))

    def search(self, promt):
        res = ""
        users = self.values()
        for user in users:
            if promt in str(user):
                res += str(user) + "\n"
        if res:
            return res  
        else:
            raise KeyError(messages.get(14))  


class BookIterator:
    book: AddressBook
    def __init__(self, book: AddressBook) -> None:
        self.book = book
    def __iter__(self):
        return self.book


def hello(promt: str):
    return messages.get(6)


@error_processor
def add(promt: str):
    arguments = promt.split(" ")
    l = len(arguments)
    match l:
        case 0:
            raise ValueError(messages.get(1))
        case 1:
            raise ValueError(messages.get(1))
        case 2:
            rec = Record(arguments[0],[ arguments[1]])
            book.add_record(rec)
            return messages.get(-1)
        case _:
            raise ValueError(messages.get(2))


@error_processor
def phone(promt: str):
    arguments = promt.split(" ")
    l = len(arguments)
    match l:
        case 0:
            raise ValueError(messages.get(1))
        case 1:
            try:
                res = ""
                for phone in book.find_user(arguments[0]).phones:
                    res += str(phone) + "\n"
                if res:
                    return res
                else:
                    raise ValueError(messages.get(4))
            except:
                raise ValueError(messages.get(4))
        case _:
            raise ValueError(messages.get(2))


@error_processor
def show_all(promt: str):
    res = ''
    res = book.show_all()
    return res


def finish(promt: str):
    return messages.get(5)


@error_processor
def days_to_bd(promt: str):
    return book.find_user(promt).days_to_birthday()

@error_processor
def search(promt: str):
    return book.search(promt)


def save_book(book: AddressBook, filename: str = "data.ph"):
    try:
        dump = pickle.dumps(book)
        f = open(filename, "wb")
        f.write(dump)
        f.close()
    except:
        print(messages.get(12))


def load_book(filename: str = "data.ph")->AddressBook:
    try:
        f = open(filename, "rb")
        data = f.read()
        res = pickle.loads(data)
        f.close()
        return res
    except:
        print(messages.get(13))


OPERATIONS = {
    'hello': hello,
    'add': add,
    'change': add,
    'phone': phone,
    'show all': show_all,
    'good bye': finish,
    'close': finish,
    'exit': finish,
    'fuck off': finish,
    'days to bd': days_to_bd,
    'search': search
}


@error_processor
def parse(promt: str):
    command = ''
    arguments = ''
    for operation in OPERATIONS.keys():
        if operation in promt.lower():
            command = str(operation)
            break
    if command != '':
        arguments = promt[len(command + ' '):]
        return OPERATIONS.get(command)(arguments)
    else:
        raise ValueError(messages.get(0))


book = load_book()

def main():
    os.system('CLS')
    print("- Hello! Let's get started!")
    while True:
        command = input()
        res = parse(command)
        print(res)
        if res == messages.get(5):
            save_book(book)
            break
        

main()