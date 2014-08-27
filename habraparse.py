#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint

from habr.topic import HabraTopic
from habr.user import HabraUser


__author__ = 'icoz'


def main():
    pass
    hu = HabraUser('icoz')
    print('getting favorites')
    favs = hu.favorites()
    # pprint(favs)
    for name in favs:
        if int(favs[name]) > 220000:
            print('===================')
            print('parsing {}...'.format(name))
            print('===================')
            t = HabraTopic(favs[name])
            pprint(t.title())
            pprint(t.author())
            pprint(t.rating())
            pprint(t.comments_count())


if __name__ == '__main__':
    main()
