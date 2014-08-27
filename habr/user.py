from copy import deepcopy
from unittest import TestCase

from lxml import html
import requests


__author__ = 'icoz'


def get_pages(doc):
    pages_data = doc.xpath("//ul[@id='nav-pages']//a[last()]")
    # print(pages_data)
    if len(pages_data) > 0:
        pg_text = str(pages_data[-1].attrib['href']).split('/')[-2]
        # print('pages=',pg_text[4:])
        pages = int(pg_text[4:])
    else:
        pages = 1
    return pages


class HabraUser(object):
    def __init__(self, username, need_favorites=False, need_user_posts=False):
        self._username = username
        self._user = dict()
        self._user_karma = dict()
        self._user_profile = dict()
        self._user_activity = dict()

        req_data = requests.get(self._genUrlForUsername(username)).text
        self._doc = html.document_fromstring(req_data)
        self._parseUserpage()
        self._user_favorites = dict()
        self._user_favorites_loaded = need_favorites
        if need_favorites:
            self._user_favorites = self._getFavorites()
        self._user_posts = dict()
        self._user_posts_loaded = need_user_posts
        if need_user_posts:
            self._user_posts = self._getUserPosts()

    def favorites(self):
        if not self._user_favorites_loaded:
            self._user_favorites = self._getFavorites()
        return deepcopy(self._user_favorites)

    def user_posts(self):
        if not self._user_posts_loaded:
            self._user_posts = self._getUserPosts()
        return deepcopy(self._user_posts)

    def profile(self):
        return deepcopy(self._user_profile)

    def activity(self):
        return deepcopy(self._user_activity)

    def karma(self):
        return deepcopy(self._user_karma)

    def _genFavoritesUrlByUser(self, username):
        '''
        Generates favirites URL using username

        :param id:
            string with username
        :return:
            string with URL
        '''
        return self._genUrlForUsername(username) + 'favorites/'
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
        cmpns = self._doc.xpath("//div[@class='user_profile']/dl[@id='favorite_companies_list']//a")
        for company in cmpns:
            out.append((company.text, company.attrib['href']))
        return out


    def _getUserHubList(self):
        out = []
        hubs = self._doc.xpath("//div[@class='user_profile']/dl[@class='hubs_list']//a[@class='cross']")
        for hub in hubs:
            out.append((hub.text, hub.attrib['href']))
        return out


    def _parseUserpage(self):

        p_tags = self._doc.xpath("//div[@class='user_profile']//ul[@id='people-tags']//a/span")
        registration_date = self._doc.xpath("//div[@class='user_profile']//dd[@class='grey']")[0].text

        self._user['username'] = self._doc.xpath("//div[@class='user_header']/h2/a").pop().text
        self._user_karma['karma'] = float(
            self._doc.xpath("//div[@class='karma']//div[@class='num']").pop().text.replace(',', '.'))
        self._user_karma['karma_vote'] = int(
            self._doc.xpath("//div[@class='karma']/div[@class='votes']").pop().text.split(' ')[0])
        self._user_karma['rating'] = float(
            self._doc.xpath("//div[@class='rating']/div[@class='num']").pop().text.replace(',', '.'))
        self._user_profile['fullname'] = self._doc.xpath(
            "//div[@class='user_profile']/div[@class='fullname']").pop().text.strip()
        self._user_karma['rating_place'] = int(
            self._doc.xpath("//div[@class='user_profile']/div[@class='rating-place']").pop().text.split('-')[0])
        if len(self._doc.xpath("//div[@class='user_profile']//dd[@class='bday']")):
            self._user_profile['birthday'] = self._doc.xpath("//div[@class='user_profile']//dd[@class='bday']")[0].text
        self._user_profile['country'] = self._doc.xpath("//div[@class='user_profile']//dd/a[@class='country-name']")[
            0].text
        self._user_profile['region'] = self._doc.xpath("//div[@class='user_profile']//dd/a[@class='region']")[0].text
        self._user_profile['city'] = self._doc.xpath("//div[@class='user_profile']//dd/a[@class='city']")[0].text
        self._user_profile['people_tags'] = [i for i in map(lambda x: x.text, p_tags)]
        self._user_profile['registraion_date'] = registration_date[:registration_date.index('\r\n')]

        self._user_activity['followers_count'] = int(
            self._doc.xpath("//div[@class='stats']/div[@id='followers_count']/a").pop().text.split(' ')[0])
        self._user_activity['posts_count'] = int(
            self._doc.xpath("//div[@class='stats']/div[@class='item posts_count']/a").pop().text.split(' ')[0])
        self._user_activity['comments_count'] = int(
            self._doc.xpath("//div[@class='stats']/div[@class='item comments_count']/a").pop().text.split(' ')[0])

        self._user['company_list'] = self._getUserCompanyList()
        self._user['hubs_list'] = self._getUserHubList()
        self._user['profile'] = self._user_profile
        self._user['activity'] = self._user_activity
        self._user['karma'] = self._user_karma


    def _getFavorites(self):
        """
        Returns list of ('topic_name', 'topic_url')

        :param username:
            string of username, ex. 'some_user'
        :return:
            list of ('topic_name', 'topic_id')
        """
        url = self._genFavoritesUrlByUser(self._username)
        doc = html.document_fromstring(requests.get(url).text)
        out = dict()
        pages = get_pages(doc)
        favs = doc.xpath("//div[@class='user_favorites']//a[@class='post_title']")
        for f in favs:
            out[f.text] = f.attrib['href'][-7:-1]
        for p in range(2, pages):
            url = 'http://habrahabr.ru/users/{0}/favorites/page{1}/'.format(self._username, p)
            # if show_progress:
            # print('parsing page{0}... url={1}'.format(p, url))
            doc = html.document_fromstring(requests.get(url).text)
            favs = doc.xpath("//div[@class='user_favorites']//a[@class='post_title']")
            for f in favs:
                out[f.text] = f.attrib['href'][-7:-1]
        return out

    def _getUserPosts(self):
        url = self._genUrlForUsername(self._username) + 'topics/'
        req = requests.get(url)
        if req.status_code != 200:
            raise IOError('doc not found. URL = {}'.format(url))
        doc = html.document_fromstring(req.text)
        out = dict()
        pages = get_pages(doc)
        posts = doc.xpath("//div[@class='posts_list']//a[@class='post_title']")
        for f in posts:
            # print(f.text)
            out[f.text] = f.attrib['href'][-7:-1]
        for p in range(2, pages):
            url = self._genUrlForUsername(self._username) + 'topics/page{0}/'.format(p)
            req = requests.get(url)
            if req.status_code != 200:
                raise IOError('doc not found. URL = {}'.format(url))
            doc = html.document_fromstring(req.text)
            posts = doc.xpath("//div[@class='posts_list']//a[@class='post_title']")
            for f in posts:
                out[f.text] = f.attrib['href'][-7:-1]
        return out


import pprint


class Test_HabraUser(TestCase):
    def setUp(self):
        self.hu = HabraUser('icoz')
        pass

    def test_parseUserpage(self):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.hu.activity())
        pp.pprint(self.hu.profile())
        pp.pprint(self.hu.karma())

    def test_favs(self):
        pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(self.hu.favorites())

    def test_user_posts(self):
        hu = HabraUser('Zelenyikot')
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint('userposts=')
        pp.pprint(hu.user_posts())
        # out = getFavForUsername('icoz')
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(out)

