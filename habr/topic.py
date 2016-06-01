from copy import deepcopy
from unittest import TestCase

import requests
from lxml import etree, html

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
        hubs = doc.xpath("//div[@class='hubs']/a")
        for h in hubs:
            self.post['hubs'].append((h.text, h.attrib['href']))
        post_title = doc.xpath('//h1[@class="post__title"]/span')
        if len(post_title) == 0:
            raise PostDeleted
        self.post['title'] = post_title
        tmp = doc.xpath("//div[@class='author-info__username']//a[@class='author-info__nickname']") or \
              doc.xpath("//div[@class='author-info__username']//a[@class='author-info__name']") or \
              doc.xpath("//div[@class='author-info__username']//span[@class='author-info__name']")
        self.post['author'] = tmp[0].text if len(tmp) else ''
        # bug in class 'infopanel ' - space added
        tmp = doc.xpath(
            "//ul[@class='postinfo-panel postinfo-panel_post']//span[@class='oting-wjt__counter-score js-score']")
        self.post['rating'] = tmp[0].text if len(tmp) else ''
        tmp = doc.xpath("//div[@class='content html_format']")
        self.post['text'] = etree.tostring(tmp[0], pretty_print=True, method='html').decode('utf-8') \
            if len(tmp) else ''
        self.post['comments'] = []
        # bug in class 'comments_list ' - space added
        # comments = doc.xpath("//div[@class='comments_list ']//div[@class='comment_item']")
        # comments = doc.xpath("//ul[@id='comments-list']//li[@class='comment_item']")
        # record = (author, text)
        authors = list(map(lambda x: x.text, doc.xpath("//ul[@id='comments-list']//a[@class='comment-item__username']")))
        cmt_texts = list(map(lambda x: x.text.strip(), doc.xpath("//ul[@id='comments-list']//div[starts-with(@class,'message html_format ')]")))
        c_id = list(map(lambda x: int(x.attrib['id'][8:]), doc.xpath("//ul[@id='comments-list']//li[@class='comment_item']")))
        p_id = list(map(lambda x: int(x.attrib['data-parent_id']), doc.xpath("//ul[@id='comments-list']//span[@class='parent_id']")))
        time = list(map(lambda x: x.text.strip(), doc.xpath("//ul[@id='comments-list']//time")))
        tpl = tuple(zip(authors, cmt_texts, c_id, p_id, time))
        self.post['comments'] = tuple(
            map(
                lambda x:
                    {
                        'author':x[0],
                        'text': x[1],
                        'c_id': x[2],
                        'p_id': x[3],
                        'time': x[4],
                    },
                tpl)
        )
        self.post['comments_count'] = len(self.post['comments'])

        # self.post['comments'] = list()
        # for c in comments:
        #     # self.post['comments'].append(etree.tostring(c, pretty_print=True, method='html').decode('utf-8'))
        #     # record = (author, text, c_id, parent_c_id)
        #     author = c.xpath("//a[@class='comment-item__username']")
        #     if len(author): author = author[0].text
        #     else: author = '<anonymous>'
        #     text = c.xpath("//div[@class='message html_format ']")
        #     if text != '': text = text[0].text
        #     c_id = c.attrib['id']
        #     p_id = c.xpath("//span[@class='parent_id']")[0]
        #     if p_id != '': p_id = p_id.attrib['data-parent_id']
        #     self.post['comments'].append((author, text, c_id, p_id))

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
        self.post['title'] = self.post['title'][1].text


class GeektimesTopic(TMTopic):
    def __init__(self, topic_id):
        super().__init__(topic_id, domain='geektimes.ru')
        self.post['title'] = self.post['title'][0].text


# R.I.P.
# class MegamozgTopic(TMTopic):
#     def __init__(self, topic_id):
#         super().__init__(topic_id, domain='megamozg.ru')


import pprint


class TestHabraTopic(TestCase):
    def test_topic(self):
        t = HabraTopic(231957)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(t.author())
        self.assertEqual(t.author(), 'Яндекс')
        pp.pprint(t.title())
        self.assertEqual(t.title(), 'Memory management в ядре Linux. Семинар в Яндексе')
        pp.pprint(t.post['comments_count'])
        pp.pprint(t.post['rating'])

    def test_topic2(self):
        t = HabraTopic(208802)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(t.author())
        self.assertEqual(t.author(), '@icoz')
        self.assertEqual(t.title(), 'Экспорт Избранного на Хабре в PDF')
        pp.pprint(t.title())
        pp.pprint(t.post['comments_count'])
        pp.pprint(t.post['rating'])
        self.assertEqual(t.comments()[0][0], 'keccak')
        self.assertEqual(t.comments()[1][0], 'icoz')

    def test_topic3(self):
        t = HabraTopic(28108)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(t.author())
        self.assertEqual(t.author(), '@cachealot')
        self.assertEqual(t.title(), 'эффективное использование vim: «from the very begining»')
        pp.pprint(t.title())
        pp.pprint(t.post['comments_count'])
        pp.pprint(t.post['rating'])
        self.assertEqual(t.comments()[0][0], 'cachealot')
        self.assertEqual(t.comments()[0][1], 'не поверите, 3,5 часа убил на пост )')
        self.assertEqual(t.comments()[0][2], 734629)
        self.assertEqual(t.comments()[0][3], 0)
        self.assertEqual(t.comments()[1][0], 'ShPashok')
        self.assertEqual(t.comments()[1][1], 'а 2 секунды на хабракат пожалели :)')
        self.assertEqual(t.comments()[1][2], 734630)
        self.assertEqual(t.comments()[1][3], 734629)


class TestGTTopic(TestCase):
    def test_topic(self):
        t = GeektimesTopic(243447)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(t.author())
        self.assertEqual(t.author(), 'Soundpal')
        pp.pprint(t.title())
        self.assertEqual(t.title(), 'На что влияет сопротивление наушников')
        pp.pprint(t.post['comments_count'])
        pp.pprint(t.post['rating'])

    def test_topic2(self):
        t = GeektimesTopic(245130)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(t.author())
        self.assertEqual(t.author(), '@Robotex')
        pp.pprint(t.title())
        self.assertEqual(t.title(), 'Autodesk и Voxel8 делают 3D-печать электроники реальностью')
        pp.pprint(t.post['comments_count'])
        pp.pprint(t.post['rating'])

# class TestMMTopic(TestCase):
#     def test_topic(self):
#         t = MegamozgTopic(418)
#         pp = pprint.PrettyPrinter(indent=4)
#         pp.pprint(t.author())
#         self.assertEqual(t.author(), '@Kirilkin')
#         pp.pprint(t.title())
#         pp.pprint(t.post['comments_count'])
#         pp.pprint(t.post['rating'])
#
#     def test_topic2(self):
#         t = MegamozgTopic(8568)
#         pp = pprint.PrettyPrinter(indent=4)
#         pp.pprint(t.author())
#         self.assertEqual(t.author(), '@jasiejames')
#         pp.pprint(t.title())
#         pp.pprint(t.post['comments_count'])
#         pp.pprint(t.post['rating'])
