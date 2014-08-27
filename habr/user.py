from unittest import TestCase
from lxml import html
import requests

__author__ = 'vlad'

class HabraUser(object):
    def __init__(self, username):
        self.username = username
        self.user = dict()
        self.user_karma = dict()
        self.user_profile = dict()
        self.user_activity = dict()

        req_data = requests.get(self._genUrlForUsername(username)).text
        self.doc = html.document_fromstring(req_data)

        self.user_favorites = self._getFavorites()

    def favorites(self):
        pass

    def _genFavoritesUrlByUser(self, username):
        '''
        Generates favirites URL using username

        :param id:
            string with username
        :return:
            string with URL
        '''
        return self._genUrlForUsername(username)+'favorites/'
            # 'http://habrahabr.ru/users/{}/favorites'.format(username)

    def _genUrlForUsername(self, username):
        '''
        Generates user-page URL using username

        :param id:
            string with username
        :return:
            string with URL
        '''
        return 'http://habrahabr.ru/users/{}/'.format(username)


    def _getUserCompanyList(self):
        out = []
        cmpns = self.doc.xpath("//div[@class='user_profile']/dl[@id='favorite_companies_list']//a")
        for company in cmpns:
            out.append((company.text, company.attrib['href']))
        return out


    def _getUserHubList(self):
        out = []
        hubs = self.doc.xpath("//div[@class='user_profile']/dl[@class='hubs_list']//a[@class='cross']")
        for hub in hubs:
            out.append((hub.text, hub.attrib['href']))
        return out


    def _parseUserpage(self, url):

        p_tags = self.doc.xpath("//div[@class='user_profile']//ul[@id='people-tags']//a/span")
        registration_date = self.doc.xpath("//div[@class='user_profile']//dd[@class='grey']")[0].text

        self.user['username'] = self.doc.xpath("//div[@class='user_header']/h2/a").pop().text
        self.user_karma['karma'] = float(self.doc.xpath("//div[@class='karma']//div[@class='num']").pop().text.replace(',', '.'))
        self.user_karma['karma_vote'] = int(self.doc.xpath("//div[@class='karma']/div[@class='votes']").pop().text.split(' ')[0])
        self.user_karma['rating'] = float(self.doc.xpath("//div[@class='rating']/div[@class='num']").pop().text.replace(',', '.'))
        self.user_profile['fullname'] = self.doc.xpath("//div[@class='user_profile']/div[@class='fullname']").pop().text.strip()
        self.user_karma['rating_place'] = int(
            self.doc.xpath("//div[@class='user_profile']/div[@class='rating-place']").pop().text.split('-')[0])
        self.user_profile['birthday'] = self.doc.xpath("//div[@class='user_profile']//dd[@class='bday']")[0].text
        self.user_profile['country'] = self.doc.xpath("//div[@class='user_profile']//dd/a[@class='country-name']")[0].text
        self.user_profile['region'] = self.doc.xpath("//div[@class='user_profile']//dd/a[@class='region']")[0].text
        self.user_profile['city'] = self.doc.xpath("//div[@class='user_profile']//dd/a[@class='city']")[0].text
        self.user_profile['people_tags'] = [i for i in map(lambda x: x.text, p_tags)]
        self.user_profile['registraion_date'] = registration_date[:registration_date.index('\r\n')]

        self.user_activity['followers_count'] = int(
            self.doc.xpath("//div[@class='stats']/div[@id='followers_count']/a").pop().text.split(' ')[0])
        self.user_activity['posts_count'] = int(
            self.doc.xpath("//div[@class='stats']/div[@class='item posts_count']/a").pop().text.split(' ')[0])
        self.user_activity['comments_count'] = int(
            self.doc.xpath("//div[@class='stats']/div[@class='item comments_count']/a").pop().text.split(' ')[0])

        self.user['company_list'] = self._getUserCompanyList()
        self.user['hubs_list'] = self._getUserHubList()
        self.user['profile'] = self.user_profile
        self.user['activity'] = self.user_activity
        self.user['karma'] = self.user_karma


    def _getFavorites(self, show_progress = False):
        """
        Returns list of ('topic_name', 'topic_url')

        :param username:
            string of username, ex. 'some_user'
        :return:
            list of ('topic_name', 'topic_id')
        """
        url = self._genFavoritesUrlByUser(self.username)
        doc = html.document_fromstring(requests.get(url).text)
        out = dict()
        pages = int(doc.xpath("//ul[@id='nav-pages']//noindex/a")[-1].attrib['href'][-3:-1])
        favs = doc.xpath("//div[@class='user_favorites']//a[@class='post_title']")
        for f in favs:
            out[f.text] = f.attrib['href'][-7:-1]
        for p in range(2, pages):
            url = 'http://habrahabr.ru/users/{0}/favorites/page{1}/'.format(self.username, p)
            if show_progress:
                print('parsing page{0}... url={1}'.format(p,url))
            doc = html.document_fromstring(requests.get(url).text)
            favs = doc.xpath("//div[@class='user_favorites']//a[@class='post_title']")
            for f in favs:
                out[f.text] = f.attrib['href'][-7:-1]
        return out

import pprint

class Test_HabraUser(TestCase):
    def setUp(self):
        pass

    def test_parseUserpage(self):
        hu = HabraUser('icoz')
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(hu.user_favorites)

    def test_favs(self):
        pass
        # out = getFavForUsername('icoz')
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(out)


