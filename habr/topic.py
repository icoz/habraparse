from copy import deepcopy
from unittest import TestCase

from lxml import etree, html
import requests


__author__ = 'icoz'


class PostDeleted(Exception):
    pass


class TMTopic(object):
    def __init__(self, topic_id, domain='habrahabr.ru'):
        '''
        init
        :param topic_id: str or int with topic id
        :return:
        '''
        self.domain = domain
        if isinstance(topic_id, (str, int)):
            self.post = dict()
            self._topic_id = topic_id
            self.url = self._getTopicUrl(topic_id)
            self._parseTopic()
        else:
            raise TypeError('topic_id must be str or int!')

    def getTopicUrl(self):
        return self.url

    def _getTopicUrl(self, topic_id):
        return str('http://{domain}/post/{tid}/').format(domain=self.domain, tid=topic_id)

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
        post_title = doc.xpath("//span[@class='post_title']")
        if len(post_title) == 0:
            raise PostDeleted
        self.post['title'] = post_title[0].text
        tmp = doc.xpath("//div[@class='author']/a")
        self.post['author'] = tmp[0].text if len(tmp) > 0 else ''
        # bug in class 'infopanel ' - space added
        tmp = doc.xpath("//div[@class='infopanel ']//span[@class='score']")
        self.post['rating'] = tmp[0].text if len(tmp) > 0 else ''
        tmp = doc.xpath("//div[@class='content html_format']")
        self.post['text'] = etree.tostring(tmp[0], pretty_print=True, method='html').decode('utf-8') \
                            if len(tmp) > 0 else ''
        self.post['comments'] = []
        # bug in class 'comments_list ' - space added
        comments = doc.xpath("//div[@class='comments_list ']//div[@class='comment_item']")
        self.post['comments_count'] = len(comments)
        for c in comments:
            self.post['comments'].append(etree.tostring(c, pretty_print=True, method='html').decode('utf-8'))

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

    def post_id(self):
        return self._topic_id


class HabraTopic(TMTopic):
    def __init__(self, topic_id):
        super().__init__(topic_id, domain='habrahabr.ru')


class GeektimesTopic(TMTopic):
    def __init__(self, topic_id):
        super().__init__(topic_id, domain='geektimes.ru')


class MegamozgTopic(TMTopic):
    def __init__(self, topic_id):
        super().__init__(topic_id, domain='megamozg.ru')


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


class TestGTTopic(TestCase):
    def test_topic(self):
        t = GeektimesTopic(243447)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(t.author())
        self.assertEqual(t.author(), 'SOUNDPAL')
        pp.pprint(t.title())
        pp.pprint(t.post['comments_count'])
        pp.pprint(t.post['rating'])

    def test_topic2(self):
        t = GeektimesTopic(245130)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(t.author())
        self.assertEqual(t.author(), 'Robotex')
        pp.pprint(t.title())
        pp.pprint(t.post['comments_count'])
        pp.pprint(t.post['rating'])


class TestMMTopic(TestCase):
    def test_topic(self):
        t = MegamozgTopic(418)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(t.author())
        self.assertEqual(t.author(), 'Kirilkin')
        pp.pprint(t.title())
        pp.pprint(t.post['comments_count'])
        pp.pprint(t.post['rating'])

    def test_topic2(self):
        t = MegamozgTopic(8568)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(t.author())
        self.assertEqual(t.author(), 'jasiejames')
        pp.pprint(t.title())
        pp.pprint(t.post['comments_count'])
        pp.pprint(t.post['rating'])
