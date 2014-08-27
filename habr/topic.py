from copy import deepcopy
from unittest import TestCase

from lxml import etree, html
import requests


__author__ = 'icoz'


class HabraTopic(object):
    def __init__(self, topic_id):
        '''
        init
        :param topic_id: str or int with topic id
        :return:
        '''
        if isinstance(topic_id, (str, int)):
            self.url = str('http://habrahabr.ru/post/{}/').format(topic_id)
            self.post = dict()
            self._parseTopic()
        else:
            raise TypeError('topic_id must be str or int!')

    def _parseTopic(self):
        '''
        returns info
        '''
        self.post = dict()
        req = requests.get(self.url)
        if req.status_code != 200:
            raise IOError('Not loaded! {} gives status_code={}'.format(self.url, req.status_code))
        doc = html.document_fromstring(req.text)
        self.post['hubs'] = []
        hubs = doc.xpath("//div[@class='post_show']//div[@class='hubs']/a")
        for h in hubs:
            self.post['hubs'].append((h.text, h.attrib['href']))
        self.post['title'] = doc.xpath("//span[@class='post_title']")[0].text
        self.post['author'] = doc.xpath("//div[@class='author']/a")[0].text
        self.post['rating'] = doc.xpath("//div[@class='infopanel ']//span[@class='score']")[0].text
        self.post['text'] = etree.tostring(doc.xpath("//div[@class='content html_format']")[0], pretty_print=True)
        self.post['comments'] = []
        # bug in class 'comments_list ' - space added
        comments = doc.xpath("//div[@class='comments_list ']//div[@class='comment_item']")
        self.post['comments_count'] = len(comments)
        for c in comments:
            self.post['comments'].append(etree.tostring(c))

    def author(self):
        return deepcopy(self.post['author'])

    def text(self):
        return deepcopy(self.post['text'])


    def title(self):
        return deepcopy(self.post['title'])


    def rating(self):
        return deepcopy(self.post['rating'])

    def comments(self):
        return deepcopy(self.post['comments'])

    def comments_count(self):
        return deepcopy(self.post['comments_count'])


import pprint


class TestHabraTopic(TestCase):
    def test_topic(self):
        t = HabraTopic(231957)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(t.author())
        self.assertEqual(t.author(), 'yaklamm')
        pp.pprint(t.title())
        pp.pprint(t.post['comments_count'])
        pp.pprint(t.post['rating'])

    def test_topic2(self):
        t = HabraTopic(208802)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(t.author())
        self.assertEqual(t.author(), 'icoz')
        pp.pprint(t.title())
        pp.pprint(t.post['comments_count'])
        pp.pprint(t.post['rating'])
