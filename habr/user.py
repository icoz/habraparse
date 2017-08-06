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


class TMUser(object):
    def __init__(self, username, need_favorites=False, need_user_posts=False, domain='habrahabr.ru'):
        self._domain = domain
        self._username = username
        self._user = dict()
        self._user_karma = dict()
        self._user_profile = dict()
        self._user_activity = dict()

        # print(self._genUrlForUsername(username))
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
        """
        Returns dict by name of topic_id

        :param username:
            string of username, ex. 'some_user'
        :return:
            dict(name) = id
        """
        if not self._user_favorites_loaded:
            self._user_favorites = self._getFavorites()
            self._user_favorites_loaded = True
        return deepcopy(self._user_favorites)

    def user_posts(self):
        if not self._user_posts_loaded:
            self._user_posts = self._getUserPosts()
            self._user_posts_loaded = True
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

    def _genUrlForUsername(self, username):
        '''
        Generates user-page URL using username

        :param id:
            string with username
        :return:
            string with URL
        '''
        return 'http://{domain}/users/{username}/'.format(domain=self._domain, username=username)


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
        # print(self._doc)
        # check for BAN
        val = self._doc.xpath("//div[@class='main']/h1")
        if val and val[0].text.strip() == "Доступ закрыт":
            # maybe raise ERROR???
            return
        p_tags = self._doc.xpath("//div[@class='user_profile']//ul[@id='people-tags']//a/span")
        # date_of_registration = self._doc.xpath("//div[@class='user_profile']//dd[@class='grey']")[0].text.strip()
        tmp = self._doc.xpath("//div[@class='user_profile']//p[@class='profile-section__invited']")
        date_of_registration = tmp[0].text.strip() if tmp else ""
        tmp = self._doc.xpath("//div[@class='user_profile']//dl[last()]/dd")
        date_of_last_login = tmp[0].text.strip()

        tmp = self._doc.xpath("//div[@class='user_header']/h2/a")
        self._user['username'] = tmp.pop().text if len(tmp) else self._username

        tmp = self._doc.xpath("//div[@class='karma']//div[@class='num']")
        self._user_karma['karma'] = float(tmp.pop().text.replace(',', '.').replace("–","-")) if len(tmp) else 0.0

        tmp = self._doc.xpath("//div[@class='karma']/div[@class='votes']")
        self._user_karma['karma_vote'] = int(tmp.pop().text.split(' ')[0]) if len(tmp) else 0

        tmp = self._doc.xpath("//div[@class='rating']/div[@class='num']")
        self._user_karma['rating'] = float(tmp.pop().text.replace(',', '.').replace("–","-")) if len(tmp) else 0.0

        tmp = self._doc.xpath("//div[@class='user_profile']/div[@class='fullname']")
        self._user_profile['fullname'] = tmp.pop().text.strip() if len(tmp) else ''

        tmp = self._doc.xpath("//div[@class='user_profile']/div[@class='fullname']/sup")
        self._user_profile['is_read_only'] = True if len(tmp) else False

        tmp = self._doc.xpath("//div[@class='user_profile']/div[@class='rating-place']")
        try:
            self._user_karma['rating_place'] = int(tmp.pop().text.split('-')[0]) if len(tmp) else -1
        except ValueError:
            self._user_karma['rating_place'] = -1

        tmp = self._doc.xpath("//div[@class='user_profile']//dd[@class='bday']")
        self._user_profile['birthday'] = tmp[0].text if len(tmp) else ''

        tmp = self._doc.xpath("//div[@class='user_profile']//dd/a[@class='country-name']")
        self._user_profile['country'] = tmp[0].text if len(tmp) else ''
        tmp = self._doc.xpath("//div[@class='user_profile']//dd/a[@class='region']")
        self._user_profile['region'] = tmp[0].text if len(tmp) else ''
        tmp = self._doc.xpath("//div[@class='user_profile']//dd/a[@class='city']")
        self._user_profile['city'] = tmp[0].text if len(tmp) else ''
        self._user_profile['people_tags'] = [i for i in map(lambda x: x.text, p_tags)]
        try:
            self._user_profile['registration_date'] = date_of_registration[:date_of_registration.index('\n')].strip()
        except ValueError:
            self._user_profile['registration_date'] = date_of_registration
        self._user_profile['last_login_date'] = date_of_last_login[27:] if len(date_of_last_login) > 27 else ''

        tmp = self._doc.xpath("//div[@class='stats']/div[@id='followers_count']/a")
        self._user_activity['followers_count'] = int(tmp.pop().text.split(' ')[0]) if len(tmp) else 0

        tmp = self._doc.xpath("//div[@class='stats']/div[@class='item posts_count']/a")
        self._user_activity['posts_count'] = int(tmp.pop().text.split(' ')[0]) if len(tmp) else 0

        tmp = self._doc.xpath("//div[@class='stats']/div[@class='item comments_count']/a")
        self._user_activity['comments_count'] = int(tmp.pop().text.split(' ')[0]) if len(tmp) else 0

        self._user['company_list'] = self._getUserCompanyList()
        self._user['hubs_list'] = self._getUserHubList()
        self._user['profile'] = self._user_profile
        self._user['activity'] = self._user_activity
        self._user['karma'] = self._user_karma


    def _getFavorites(self):
        """
        Returns dict by name of topic_id

        :param username:
            string of username, ex. 'some_user'
        :return:
            dict(name) = id
        """
        url = self._genFavoritesUrlByUser(self._username)
        doc = html.document_fromstring(requests.get(url).text)
        # check for BAN
        val = self._doc.xpath("//div[@class='main']/h1")
        if val and val[0].text.strip() == "Доступ закрыт":
            # maybe raise ERROR???
            return
        out = dict()
        pages = get_pages(doc)
        favs = doc.xpath("//div[@class='user_favorites']//a[@class='post__title_link']")
        for f in favs:
            # out[f.text] = str(f.attrib['href']).split('/')[-2]
            # topic_id =
            out[f.text] = str(f.attrib['href']).split('/')[-2]
        for p in range(2, pages):
            url = 'http://{0}/users/{1}/favorites/page{2}/'.format(self._domain, self._username, p)
            # if show_progress:
            # print('parsing page{0}... url={1}'.format(p, url))
            doc = html.document_fromstring(requests.get(url).text)
            favs = doc.xpath("//div[@class='user_favorites']//a[@class='post__title_link']")
            for f in favs:
                # out[f.text] = f.attrib['href'][-7:-1]
                out[f.text] = str(f.attrib['href']).split('/')[-2]
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
            out[f.text] = str(f.attrib['href']).split('/')[-2]
            # out[f.text] = f.attrib['href'][-7:-1]
        for p in range(2, pages):
            url = self._genUrlForUsername(self._username) + 'topics/page{0}/'.format(p)
            req = requests.get(url)
            if req.status_code != 200:
                raise IOError('doc not found. URL = {}'.format(url))
            doc = html.document_fromstring(req.text)
            posts = doc.xpath("//div[@class='posts_list']//a[@class='post_title']")
            for f in posts:
                out[f.text] = str(f.attrib['href']).split('/')[-2]
        return out


class HabraUser(TMUser):
    def __init__(self, username, need_favorites=False, need_user_posts=False):
        super().__init__(username, need_favorites, need_user_posts=need_user_posts, domain='habrahabr.ru')


class GeektimesUser(TMUser):
    def __init__(self, username, need_favorites=False, need_user_posts=False):
        super().__init__(username, need_favorites, need_user_posts=need_user_posts, domain='geektimes.ru')


# R.I.P.
# class MegamozgUser(TMUser):
#     def __init__(self, username, need_favorites=False, need_user_posts=False):
#         super().__init__(username, need_favorites, need_user_posts=need_user_posts, domain='megamozg.ru')


import pprint


class Test_HabraUser(TestCase):
    def setUp(self):
        self.hu = HabraUser('icoz')
        self.pp = pprint.PrettyPrinter(indent=4)
        pass

    def test_parseUserpage(self):
        self.pp.pprint(self.hu.activity())
        self.pp.pprint(self.hu.profile())
        self.pp.pprint(self.hu.karma())

    def test_favs(self):
        self.pp.pprint(self.hu.favorites())

    # def test_readonly_user(self):
    #     self.pp.pprint('starting test for readonly xvitaly')
    #     hu = HabraUser('xvitaly')
    #     self.pp.pprint('date=')
    #     self.pp.pprint(hu.profile()['registration_date'])

    def test_user_posts(self):
        hu = HabraUser('Zelenyikot')
        self.pp.pprint('userposts=')
        self.pp.pprint(hu.user_posts())

    def test_rating_place(self):
        self.pp.pprint('starting test for lokkersp')
        hu = HabraUser('lokkersp')
        self.pp.pprint('karma=')
        self.pp.pprint(hu.karma())


class Test_GeektimesUser(TestCase):
    def setUp(self):
        self.hu = GeektimesUser('icoz')
        pass

    def test_parseUserpage(self):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.hu.activity())
        pp.pprint(self.hu.profile())
        pp.pprint(self.hu.karma())

    # def test_favs(self):
    # pp = pprint.PrettyPrinter(indent=4)

    def test_user_posts(self):
        hu = GeektimesUser('Zelenyikot')
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint('userposts=')
        pp.pprint(hu.user_posts())

#
# class Test_MegamozgUser(TestCase):
#     def setUp(self):
#         self.hu = MegamozgUser('icoz')
#         pass
#
#     def test_parseUserpage(self):
#         pp = pprint.PrettyPrinter(indent=4)
#         pp.pprint(self.hu.activity())
#         pp.pprint(self.hu.profile())
#         pp.pprint(self.hu.karma())
#
#     # def test_favs(self):
#     # pp = pprint.PrettyPrinter(indent=4)
#
#     def test_user_posts(self):
#         hu = MegamozgUser('Zelenyikot')
#         pp = pprint.PrettyPrinter(indent=4)
#         pp.pprint('userposts=')
#         pp.pprint(hu.user_posts())
#
