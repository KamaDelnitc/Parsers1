import re

from DB import DBWork
import configparser
import os
config = configparser.ConfigParser()
config.read(os.getcwd() + '\\config.ini')

class TextReader:
    answer=None
    text=None
    search=None
    def __init__(self):
        self.answer=''
        self.text=''
        self.search=''
        self.con=DBWork()

    def loadText(self, text):
        self.text=text

    def checkNewmessage(self):
        self.last = self.con.get_last_message()[0]
        messages = self.bot.get_updates(offset=10)
        new_message = list(filter(lambda x: x['update_id'] > self.last, messages))
        if new_message.__len__>0:
            return True
        else:
            return False


    def readText(self):
        if (self.text in config['GREETING']['words']):
            self.answer='Здравствуйте, [username]. Я бот, который предоставляет информацию по' \
                        'фирмам. Я ищу информацию в социальных сетях, на сайте налоговой.' \
                        'Для поиска информации на сайте налоговой, укажите команду nalog {ИНН или наименование}, для' \
                        'поиска информации в Livejournal - Livejournal {Наименование}'
            self.code=0
            return self.code
        elif re.search('livejournal',self.text.lower()):
            self.search=self.text.split(' ')[1]
            if (self.search.__len__()<1):
                self.answer = 'Нет имени для поиска'
                self.code=-1
            else:
                self.answer = '[username]. Я начинаю поиск в Livejournal'
                self.code = 1
            return self.code
        elif re.search('nalog',self.text.lower()):
            self.search=self.text.split(' ')[1]
            if (self.search.__len__()<1):
                self.answer = 'Нет имени для поиска'
                self.code=-1
            else:
                self.answer = '[username]. Я начинаю поиск на сайте налоговой'
                self.code = 2
        else:
            self.answer = '[username]. Вы указали неправильный формат формат запроса'
            self.code = -1
        return self.code
