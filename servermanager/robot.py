import os
import re

import jsonpickle
from werobot import WeRoBot
from werobot.replies import ArticlesReply, Article
from django.conf import settings
from djangoblog.utils import get_sha256
from servermanager.api.blogapi import BlogApi
from servermanager.api.commonapi import TuLing
from servermanager.models import commands
from .MemcacheStorage import MemcacheStorage

robot = WeRoBot(token=os.environ.get('DJANGO_WEROBOT_TOKEN')
                or 'lylinux', enable_session=True)
memstorage = MemcacheStorage()
if memstorage.is_available:
    robot.config['SESSION_STORAGE'] = memstorage
else:
    from werobot.session.filestorage import FileStorage
    import os
    from django.conf import settings

    if os.path.exists(os.path.join(settings.BASE_DIR, 'werobot_session')):
        os.remove(os.path.join(settings.BASE_DIR, 'werobot_session'))
    robot.config['SESSION_STORAGE'] = FileStorage(filename='werobot_session')
blogapi = BlogApi()
tuling = TuLing()


def convert_to_articlereply(articles, message):
    reply = ArticlesReply(message=message)
    from blog.templatetags.blog_tags import truncatechars_content
    for post in articles:
        imgs = re.findall(r'(?:http\:|https\:)?\/\/.*\.(?:png|jpg)', post.body)
        imgurl = ''
        if imgs:
            imgurl = imgs[0]
        article = Article(
            title=post.title,
            description=truncatechars_content(post.body),
            img=imgurl,
            url=post.get_full_url()
        )
        reply.add_article(article)
    return reply


@robot.filter(re.compile(r"^\?.*"))
def search(message, session):
    s = message.content
    searchstr = str(s).replace('?', '')
    result = blogapi.search_articles(searchstr)
    if result:
        articles = list(map(lambda x: x.object, result))
        reply = convert_to_articlereply(articles, message)
        return reply
    else:
        return 'No relevant article found。'


@robot.filter(re.compile(r'^category\s*$', re.I))
def category(message, session):
    categorys = blogapi.get_category_lists()
    content = ','.join(map(lambda x: x.name, categorys))
    return 'All articleCategories：' + content


@robot.filter(re.compile(r'^recent\s*$', re.I))
def recents(message, session):
    articles = blogapi.get_recent_articles()
    if articles:
        reply = convert_to_articlereply(articles, message)
        return reply
    else:
        return "There is no article yet"


@robot.filter(re.compile('^help$', re.I))
def help(message, session):
    return '''Welcome to follow!
            By default, it will chat with the Turing robot~~
        You can get the information with the following commands
        ?Keyword search article.
        Such as ?python.
        category gets articleCategories and article number.
        category-***Get the Categoriesarticle
        Such as category-python
        recentGet the latest article
        helpGet help.
        weather: Get the weather
        Such as weather: Xi'an
        idcard: Get ID card information
        Such as idcard: 61048119xxxxxxxxxx
        music: music search
        Such as music: happy cloudy day
        PS: None of the above punctuation marks support Chinese punctuation~~          
 '''


@robot.filter(re.compile(r'^weather\:.*$', re.I))
def weather(message, session):
    return "under construction..."


@robot.filter(re.compile(r'^idcard\:.*$', re.I))
def idcard(message, session):
    return "under construction..."


@robot.handler
def echo(message, session):
    handler = MessageHandler(message, session)
    return handler.handler()


class CommandHandler():
    def __init__(self):
        self.commands = commands.objects.all()

    def run(self, title):
        cmd = list(
            filter(
                lambda x: x.title.upper() == title.upper(),
                self.commands))
        if cmd:
            return self.__run_command__(cmd[0].command)
        else:
            return "The relevant command was not found, please enter hepme for help。"

    def __run_command__(self, cmd):
        try:
            str = os.popen(cmd).read()
            return str
        except BaseException:
            return 'Command execution error!'

    def get_help(self):
        rsp = ''
        for cmd in self.commands:
            rsp += '{c}:{d}\n'.format(c=cmd.title, d=cmd.describe)
        return rsp


cmdhandler = CommandHandler()


class MessageHandler():
    def __init__(self, message, session):
        userid = message.source
        self.message = message
        self.session = session
        self.userid = userid
        try:
            info = session[userid]
            self.userinfo = jsonpickle.decode(info)
        except BaseException:
            userinfo = WxUserInfo()
            self.userinfo = userinfo

    @property
    def is_admin(self):
        return self.userinfo.isAdmin

    @property
    def is_password_set(self):
        return self.userinfo.isPasswordSet

    def savesession(self):
        info = jsonpickle.encode(self.userinfo)
        self.session[self.userid] = info

    def handler(self):
        info = self.message.content

        if self.userinfo.isAdmin and info.upper() == 'EXIT':
            self.userinfo = WxUserInfo()
            self.savesession()
            return "exit successfully"
        if info.upper() == 'ADMIN':
            self.userinfo.isAdmin = True
            self.savesession()
            return "Enter administrator password"
        if self.userinfo.isAdmin and not self.userinfo.isPasswordSet:
            passwd = settings.WXADMIN
            if settings.TESTING:
                passwd = '123'
            if passwd.upper() == get_sha256(get_sha256(info)).upper():
                self.userinfo.isPasswordSet = True
                self.savesession()
                return "Verification passed, please enter the command or the command code to be executed: enter helpme to get help"
            else:
                if self.userinfo.Count >= 3:
                    self.userinfo = WxUserInfo()
                    self.savesession()
                    return "Verification times exceeded"
                self.userinfo.Count += 1
                self.savesession()
                return "Authentication failed, please re-enter the administrator password:"
        if self.userinfo.isAdmin and self.userinfo.isPasswordSet:
            if self.userinfo.Command != '' and info.upper() == 'Y':
                return cmdhandler.run(self.userinfo.Command)
            else:
                if info.upper() == 'HELPME':
                    return cmdhandler.get_help()
                self.userinfo.Command = info
                self.savesession()
                return "Confirm execution: " + info + " Order?"
        rsp = tuling.getdata(info)
        return rsp


class WxUserInfo():
    def __init__(self):
        self.isAdmin = False
        self.isPasswordSet = False
        self.Count = 0
        self.Command = ''



@robot.handler
def hello(message, session):
    blogapi = BlogApi()
    result = blogapi.search_articles(message.content)
    if result:
        articles = list(map(lambda x: x.object, result))
        reply = convert_to_articlereply(articles, message)
        return reply
    else:
        return 'No related articles found。'

