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

