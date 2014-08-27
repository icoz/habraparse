#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase

from lxml import html, etree
import requests


__author__ = 'icoz'

'''
topic has:
post_title .text
post shortcuts_item .id = post_<id>
hubs[] -> .text
'''


def getUserCompanyList(doc):
    out = []
    cmpns = doc.xpath("//div[@class='user_profile']/dl[@id='favorite_companies_list']//a")
    for company in cmpns:
        out.append((company.text, company.attrib['href']))
    return out


def getUserHubList(doc):
    out = []
    hubs = doc.xpath("//div[@class='user_profile']/dl[@class='hubs_list']//a[@class='cross']")
    for hub in hubs:
        out.append((hub.text, hub.attrib['href']))
    return out


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
    post['hubs'] = []
    hubs = doc.xpath("//div[@class='post_show']//div[@class='hubs']/a")
    for h in hubs:
        post['hubs'].append((h.text, h.attrib['href']))
    post['title'] = doc.xpath("//span[@class='post_title']")[0].text
    post['author'] = doc.xpath("//div[@class='author']/a")[0].text
    post['text'] = etree.tostring(doc.xpath("//div[@class='content html_format']")[0], pretty_print=True)
    post['comments'] = getTopicComments(doc)
    #
    # post['author'] = getTopicAuthor(doc)
    # # post['hubs'] = getTopicHubs(doc)
    # post['title'] = getTopicTitle(doc)
    # post['text'] = getTopicText(doc)
    # post['comments'] = getTopicComments(doc)
    return post


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
    # TODO: bug in class - space added
    comments = topic.xpath("//div[@class='comments_list ']//div[@class='comment_item']")
    print(len(comments))
    cmnts = []
    for c in comments:
        cmnts.append(etree.tostring(c))
    return cmnts

def getUserInfo(user):
    pass


def genUrlForUsername(username):
    '''
    Generates user-page URL using username

    :param id:
        string with username
    :return:
        string with URL
    '''
    return 'http://habrahabr.ru/users/{}/'.format(username)

def genTopicUrlByID(id):
    '''
    Generates topic URL for id

    :param id:
        string or int
    :return:
        string with URL
    '''
    return 'http://habrahabr.ru/post/{}/'.format(id)


def genFavoritesUrlByUser(username):
    '''
    Generates favirites URL using username

    :param id:
        string with username
    :return:
        string with URL
    '''
    return genUrlForUsername(username)+'favorites/'
        # 'http://habrahabr.ru/users/{}/favorites'.format(username)


def getFavForUsername(username):
    """
    Returns list of ('topic_name', 'topic_url')

    :param username:
        string of username, ex. 'some_user'
    :return:
        list of ('topic_name', 'topic_id')
    """
    url = genFavoritesUrlByUser(username)
    doc = html.document_fromstring(requests.get(url).text)
    out = []
    pages = int(doc.xpath("//ul[@id='nav-pages']//noindex/a")[-1].attrib['href'][-3:-1])
    favs = doc.xpath("//div[@class='user_favorites']//a[@class='post_title']")
    for f in favs:
        # print(f.text, f.attrib['href'][-7:-1])
        out.append((f.text, f.attrib['href'][-7:-1]))
    for p in range(2, pages):
        url = 'http://habrahabr.ru/users/{0}/favorites/page{1}/'.format(username, p)
        # print('parsing page{0}... url={1}'.format(p,url))
        doc = html.document_fromstring(requests.get(url).text)
        favs = doc.xpath("//div[@class='user_favorites']//a[@class='post_title']")
        for f in favs:
            # print(f.text, f.attrib['href'][-7:-1])
            out.append((f.text, f.attrib['href'][-7:-1]))
    out.sort()
    return out


class TestParse(TestCase):
    def setUp(self):
        pass

    def test_parseTopic(self):
        url = 'http://habrahabr.ru/post/208802/'
        d = parseTopic(url)
        self.assertEqual(d['author'], 'icoz')
        d['hubs'].sort()
        self.assertSequenceEqual(d['hubs'], [('PDF', 'http://habrahabr.ru/hub/pdf/'),
                                             ('Python', 'http://habrahabr.ru/hub/python/')])
        self.assertEqual(d['title'], 'Экспорт Избранного на Хабре в PDF')
        # d['comments']
        print(d['text'])

    def test_parseUserpage(self):
        username = 'icoz'
        url = genUrlForUsername(username)
        user = parseUserpage(url)
        print(user)

    def test_favs(self):
        import pprint

        out = getFavForUsername('icoz')
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(out)


