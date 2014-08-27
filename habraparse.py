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



def genTopicUrlByID(id):
    '''
    Generates topic URL for id

    :param id:
        string or int
    :return:
        string with URL
    '''
    return 'http://habrahabr.ru/post/{}/'.format(id)





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

