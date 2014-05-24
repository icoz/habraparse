#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase

from lxml import html
import requests


__author__ = 'icoz'

'''
topic has:
post_title .text
post shortcuts_item .id = post_<id>
hubs[] -> .text
'''


def getUserName(doc):
    username = ''


def getUserCompanyList(doc):
    return list()


def getUserHubList(doc):
    return list()


def parseUserpage(url):
    user = dict()
    user_karma = dict()
    user_profile = dict()
    user_activity = dict()

    topic = requests.get(url).text
    doc = html.document_fromstring(topic)

    p_tags = doc.xpath("//div[@class='user_profile']//ul[@id='people-tags']//a/span")
    rdate = doc.xpath("//div[@class='user_profile']//dd[@class='grey']")[0].text

    user['username'] = doc.xpath("//div[@class='user_header']/h2/a").pop().text
    user_karma['karma'] = float(doc.xpath("//div[@class='karma']//div[@class='num']").pop().text.replace(',', '.'))
    user_karma['karma_vote'] = int(doc.xpath("//div[@class='karma']/div[@class='votes']").pop().text.split(' ')[0])
    user_karma['rating'] = float(doc.xpath("//div[@class='rating']/div[@class='num']").pop().text.replace(',', '.'))
    user_profile['fullname'] = doc.xpath("//div[@class='user_profile']/div[@class='fullname']").pop().text.strip()
    user_karma['rating_place'] = int(
        doc.xpath("//div[@class='user_profile']/div[@class='rating-place']").pop().text.split('-')[0])
    user_profile['birthday'] = doc.xpath("//div[@class='user_profile']//dd[@class='bday']")[0].text
    user_profile['country'] = doc.xpath("//div[@class='user_profile']//dd/a[@class='country-name']")[0].text
    user_profile['region'] = doc.xpath("//div[@class='user_profile']//dd/a[@class='region']")[0].text
    user_profile['city'] = doc.xpath("//div[@class='user_profile']//dd/a[@class='city']")[0].text
    user_profile['people_tags'] = [i for i in map(lambda x: x.text, p_tags)]
    user_profile['registraion_date'] = rdate[:rdate.index('\r\n')]

    user_activity['followers_count'] = int(
        doc.xpath("//div[@class='stats']/div[@id='followers_count']/a").pop().text.split(' ')[0])
    user_activity['posts_count'] = int(
        doc.xpath("//div[@class='stats']/div[@class='item posts_count']/a").pop().text.split(' ')[0])
    user_activity['comments_count'] = int(
        doc.xpath("//div[@class='stats']/div[@class='item comments_count']/a").pop().text.split(' ')[0])

    user['company_list'] = getUserCompanyList(doc)
    user['hubs_list'] = getUserHubList(doc)
    user['profile'] = user_profile
    user['activity'] = user_activity
    user['karma'] = user_karma
    return user


def parseTopic(url):
    '''
    returns info
    '''
    post = dict()
    topic = requests.get(url).text
    doc = html.document_fromstring(topic)
    post['author'] = getTopicAuthor(doc)
    post['hubs'] = getTopicHubs(doc)
    post['title'] = getTopicTitle(doc)
    post['text'] = getTopicText(doc)
    post['comments'] = getTopicComments(doc)
    return post


def getTopicHubs(topic):
    try:
        hubs = []
        div = topic.find_class('hubs')[0]
        for link in div.iterlinks():
            hubs.append(link[0].text)
        return hubs
    except:
        return None


def getTopicAuthor(topic):
    try:
        div = topic.find_class('author')[0]
        links = [l for l in div.iterlinks()]
        author = links[0][0].text
        return author
    except:
        return None


def getTopicText(topic):
    pass


def getTopicTitle(topic):
    return topic.find_class('post_title')[0].text


def getTopicComments(topic):
    pass


def getUserInfo(user):
    pass


def getUrlForUsername(username):
    return 'http://habrahabr.ru/users/{}/'.format(username)


class TestParse(TestCase):
    def setUp(self):
        pass

    def test_parseTopic(self):
        url = 'http://habrahabr.ru/post/208802/'
        d = parseTopic(url)
        self.assertEqual(d['author'], 'icoz')
        d['hubs'].sort()
        self.assertSequenceEqual(d['hubs'], ['PDF', 'Python'])
        self.assertEqual(d['title'], 'Экспорт Избранного на Хабре в PDF')
        # d['comments']

    def test_parseUserpage(self):
        username = 'icoz'
        url = getUrlForUsername(username)
        user = parseUserpage(url)
        print(user)
