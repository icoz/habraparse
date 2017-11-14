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
        return str('https://{domain}/post/{tid}/').format(domain=self.domain, tid=topic_id)

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
        post_title = doc.xpath('//h1[@class="post__title"]/span') or \
                     doc.xpath('//h1[@class="megapost-head__title"]') or \
                     doc.xpath('//h1[@class="post__title post__title_full"]/span[@class="post__title-text"]')
        if len(post_title) == 0:
            raise PostDeleted('Post Deleted! {} gives status_code={}'.format(self.url, req.status_code))
        self.post['title'] = post_title
        tmp = \
            doc.xpath("//a[@class='post-type__value post-type__value_author']") or \
            doc.xpath("//div[@class='author-info__username']//a[@class='author-info__nickname']") or \
            doc.xpath("//div[@class='author-info__username']//a[@class='author-info__name']") or \
            doc.xpath("//div[@class='author-info__username']//span[@class='author-info__name']") or \
            doc.xpath("//div[@class='page-header__info']//span[@class='page-header__info-title']") or \
            doc.xpath("//header[@class='post__meta']//span[@class='user-info__nickname user-info__nickname_small']")
        if len(tmp):
            self.post['author'] = tmp[0].text
            self.post['author_url'] = ('https://' + self.domain + tmp[0].attrib['href'] ) if 'href' in tmp[0].attrib else ''
        else:
            self.post['author_url']= ''
            self.post['author'] = ''
        ###
        post_desc = doc.xpath("//meta[@name='description']/@content")
        self.post['desc'] = post_desc[0].strip("\r\n")
        #
        tmp = doc.xpath("//link[@rel='stylesheet'][@media='all']")
        style = '\n'.join([ str(etree.tostring(st,pretty_print=True, method='html').decode('utf-8')).strip("\n\r") for st in tmp ])
        self.post['styles'] = style if len(style)>2 else ''
        #
        #tmp = doc.xpath("//style[@type='text/css']")
        #style =''.join([ str(etree.tostring(st,pretty_print=True, method='html').decode('utf-8')) for st in tmp ])
        #self.post['styles'] += style if (len(style)>2) else ''
        #
        post_keywords = doc.xpath("//meta[@name='keywords']/@content")
        self.post['keywords'] = post_keywords[0].strip("\r\n") if len(post_keywords) else ''
        ###
        # bug in class 'infopanel ' - space added
        tmp = doc.xpath(
            "//ul[@class='postinfo-panel postinfo-panel_post']//span[@class='oting-wjt__counter-score js-score']")
        self.post['rating'] = tmp[0].text if len(tmp) else ''
        # tmp = doc.xpath("//div[@class='content html_format js-mediator-article']") or \
        #       doc.xpath('//div[@class="article__body js-mediator-article"]') or \
        tmp = doc.xpath('//div[@class="post__text post__text-html js-mediator-article"]')
        self.post['text'] = etree.tostring(tmp[0], pretty_print=True, method='html').decode('utf-8') if len(tmp) else ''
        # get comments
        self.post['comments'] = []
        for cmnt in doc.xpath("//ul[@id='comments-list']//li[@class='content-list__item content-list__item_comment js-comment ']"):
            try:
                self.post['comments'].append(
                    {
                        'author': cmnt.find_class("user-info__nickname")[0].text, # if cmnt.find_class("user-info__nickname") else "",
                        'text': etree.tostring(cmnt.find_class('comment__message')[0], pretty_print=True, method='html').decode('utf-8').strip(), # if cmnt.find_class('comment__message') else "",
                        # 'text': cmnt.find_class('comment__message')[0].text, # if cmnt.find_class('comment__message') else "",
                        'c_id': int(cmnt.attrib['rel']),
                        'p_id': int(cmnt.find_class("parent_id")[0].attrib['data-parent_id']),
                        'time': cmnt.find_class('comment__date-time')[0].text
                    }
                )
            except:
                print('err=',cmnt.attrib['rel'])
                pass
        self.post['comments_count'] = len(self.post['comments'])

    def author(self):
        return deepcopy(self.post['author'])
###
    def author_url(self):
        return deepcopy(self.post['author_url'])

    def desc(self):
        return deepcopy(self.post['desc'])

    def styles(self):
        return deepcopy(self.post['styles'])

    def keywords(self):
        return deepcopy(self.post['keywords'])
###
    def text(self):
        return deepcopy(self.post['text'])

    def title(self):
        return deepcopy(self.post['title'])

    def rating(self):
        return deepcopy(self.post['rating'])

    def comments(self):
        return deepcopy(tuple(self.post['comments']))

    def comments_count(self):
        return deepcopy(self.post['comments_count'])

    def post_id(self):
        return self._topic_id


class HabraTopic(TMTopic):
    def __init__(self, topic_id):
        super().__init__(topic_id, domain='habrahabr.ru')
        self.post['title'] = self.post['title'][0].text


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
        self.assertEqual(t.author(), 'yaklamm')
        pp.pprint(t.title())
        self.assertEqual(t.title(), 'Memory management в ядре Linux. Семинар в Яндексе')
        pp.pprint(t.post['comments_count'])
        pp.pprint(t.post['rating'])

    def test_topic2(self):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint("Start for post 208802")
        t = HabraTopic(208802)
        pp.pprint(t.author())
        self.assertEqual(t.author(), 'icoz')
        self.assertEqual(t.title(), 'Экспорт Избранного на Хабре в PDF')
        pp.pprint(t.title())
        pp.pprint(t.post['comments_count'])
        pp.pprint(t.post['rating'])
        # pp.pprint(t.comments())
        # pp.pprint(t.comments()[1])
        self.assertEqual(t.comments()[0]['author'], 'keccak')
        self.assertEqual(t.comments()[1]['author'], 'icoz')

    def test_topic3(self):
        t = HabraTopic(28108)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(t.author())
        self.assertEqual(t.author(), 'cachealot')
        self.assertEqual(t.title(), 'эффективное использование vim: «from the very begining»')
        pp.pprint(t.title())
        pp.pprint(t.post['comments_count'])
        pp.pprint(t.post['rating'])
        self.assertEqual(t.comments()[0]['author'], 'cachealot')
        from lxml import html
        txt = html.fromstring(t.comments()[0]['text']).text_content().replace("'",'').strip()
        self.assertEqual(txt, 'не поверите, 3,5 часа убил на пост )')
        self.assertEqual(t.comments()[0]['c_id'], 734629)
        self.assertEqual(t.comments()[0]['p_id'], 0)
        self.assertEqual(t.comments()[1]['author'], 'ShPashok')
        txt = html.fromstring(t.comments()[1]['text']).text_content().replace("'",'').strip()
        self.assertEqual(txt, 'а 2 секунды на хабракат пожалели :)')
        self.assertEqual(t.comments()[1]['c_id'], 734630)
        self.assertEqual(t.comments()[1]['p_id'], 734629)

    def test_topic4(self):
        t = HabraTopic(330358)
        self.assertEqual(t.title(), 'Rapid STP')

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

    # def test_topic2(self):
    #     t = GeektimesTopic(245130)
    #     pp = pprint.PrettyPrinter(indent=4)
    #     pp.pprint(t.author())
    #     self.assertEqual(t.author(), '@Robotex')
    #     pp.pprint(t.title())
    #     self.assertEqual(t.title(), 'Autodesk и Voxel8 делают 3D-печать электроники реальностью')
    #     pp.pprint(t.post['comments_count'])
    #     pp.pprint(t.post['rating'])

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
