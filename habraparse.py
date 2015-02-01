#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

from weasyprint import HTML, CSS

from habr.topic import HabraTopic, PostDeleted
from habr.user import HabraUser


__author__ = 'icoz'


def prepare_html(topic_id, with_comments=False):
    t = HabraTopic(str(topic_id))
    # <link href="http://habrahabr.ru/styles/1412005750/printer.css" rel="stylesheet" media="print" />
    # <link href="http://habrahabr.ru/styles/1412005750/assets/global_main.css" rel="stylesheet" media="all" />
    html_head = '''
    <html>
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <meta charset="UTF-8">
    <link href="http://habrahabr.ru/styles/1412005750/assets/post_common_css.css" rel="stylesheet" media="all" />
    <title>{title}</title>
    </head>
    <body>
    <div id="layout">
    <div class="inner">
        <div class="content_left">
            <div class="post_show">
                <div class="post shortcuts_item">
                    <h1 class="title"><span class="post_title">{title}</span></h1>
                    <div class="author">
                        <a title="Автор текста" href="http://habrahabr.ru/users/{author}/" >{author}</a>
                    </div>
                    {text}
                </div>
            </div>
    '''
    html_cmnts = '''
            <div id="comments" class="comments_list">
            <h2 class="title">Комментарии</h2>
            {comments}
            </div>
    '''
    html_foot = '''
        </div>
    </div>
    </div>
    </body>
    </html>
    '''
    html_format = html_head + html_foot
    cmnts = ''
    if with_comments:
        html_format = html_head + html_cmnts + html_foot
        for c in t.comments():
            cmnts += '{}\n'.format(c)
        html = html_format.format(title=t.title(), author=t.author(), text=t.text(), comments=cmnts)
    else:
        html = html_format.format(title=t.title(), author=t.author(), text=t.text())
    html = str(html).replace('//habrastorage.org', 'http://habrastorage.org')
    html = str(html).replace('http:http:', 'http:')
    return html


def save_html(topic_id, filename, with_comments=False):
    dir = os.path.dirname(filename)
    dir_imgs = filename + '.files'
    if dir != '' and not os.path.exists(dir):
        os.mkdir(dir)
    if not os.path.exists(dir_imgs):
        os.mkdir(dir_imgs)
    with open(filename, "wt") as f:
        html = prepare_html(topic_id, with_comments=with_comments)
        f.write(html)
        # TODO: get all images and css
        # we need to get all links to img, css, js
        # download them to dir
        # and replace it


def save_pdf(topic_id, filename, with_comments=False):
    import logging

    logger = logging.getLogger('weasyprint')
    logger.handlers = []  # Remove the default stderr handler
    logger.addHandler(logging.FileHandler('pdf_weasyprint.log'))
    dir = os.path.dirname(filename)
    if dir != '' and not os.path.exists(dir):
        os.mkdir(dir)
    html = prepare_html(topic_id, with_comments=with_comments)
    css = CSS(string='@page { size: A4; margin: 1cm !important}')
    HTML(string=html).write_pdf(filename, stylesheets=[css])


def save_all_favs_for_user(username, out_dir, save_in_html=True, with_comments=False, save_by_name=False, limit=None):
    filetype = 'pdf'
    if save_in_html:
        filetype = 'html'
        # raise NotImplemented
    hu = HabraUser(username, need_favorites=True)
    favs_id = hu.favorites()
    deleted = list()
    if limit is not None:
        limit_cnt = int(limit)
    else:
        limit_cnt = -1
    for topic_name in favs_id:
        if limit_cnt == 0:
            break
        elif limit_cnt > 0:
            limit_cnt -= 1
        topic_id = favs_id[topic_name]
        print('Downloading "{}"...'.format(topic_name))
        # topic = HabraTopic(topic_id)
        if save_by_name:
            t_name = topic_name.replace('/', '_').replace('\\', '_').replace('!', '.')
            filename = '{dir}/{name}.{filetype}'.format(dir=out_dir, name=t_name, filetype=filetype)
        else:
            filename = '{dir}/{id}.{filetype}'.format(dir=out_dir, id=topic_id, filetype=filetype)
        print('Saving it in "{}"'.format(filename))
        try:
            if save_in_html:
                html = save_html(topic_id, filename, with_comments=with_comments)
            else:
                save_pdf(topic_id, filename, with_comments=with_comments)
        except PostDeleted:
            print('Post {} is deleted!'.format(topic_id))
            deleted.append(topic_id)
    if len(deleted):
        print('All deleted posts: \n{}'.format('\n'.join(deleted)))
    pass


def save_all_user_posts(username, out_dir, save_in_pdf=False):
    raise NotImplemented
    # if save_in_pdf:
    # raise NotImplemented
    # hu = HabraUser(username, need_user_posts=True)
    # pass


def create_url_list(username, filename):
    hu = HabraUser(username)
    urls = list()
    favs_id = hu.favorites()
    for topic_name in favs_id:
        urls.append(HabraTopic.getTopicUrl(favs_id[topic_name]))
    urls.sort()
    with open(filename, 'wt') as f:
        f.write('\n'.join(urls))


import docopt


def main():
    params = """Usage:
        {prog} save_favs_list <username> <out_file>
        {prog} save_favs [-c --limit=N] <username> <out_dir>
        {prog} save_post [-c] <topic_id> <out_file>
        {prog} save_posts [-c --limit=N] <username> <out_dir>

    Arguments:
        username  Имя пользовтеля Habrahabr.ru
        out_file  Имя файла для сохранения списка избранного пользователя username
        out_dir   Путь для сохранения избранного

    Options:
        --save-html          Сохранить в HTML (по умолчанию, в PDF)
        --save-by-name       Сохранять с именем, полученным из названия статьи (по умолчанию - по ID статьи)
        -c, --with-comments     Сохранить вместе с коментариями
        --limit=N          Ограничить количество в N статей
    """.format(prog=sys.argv[0])
    try:
        args = docopt.docopt(params)
        # print(args)  # debug
        if args['save_favs_list']:
            create_url_list(args['<username>'], args['<out_file>'])
            return
        if args['save_favs']:
            save_all_favs_for_user(args['<username>'], args['<out_dir>'], save_in_html=args['--save-html'],
                                   with_comments=args['--with-comments'], save_by_name=args['--save-by-name'],
                                   limit=args['--limit'])
            return
        if args['save_post']:
            t_id = args['<topic_id>']
            fname = args['<out_file>']
            if args['--save-html']:
                save_html(t_id, filename=fname, with_comments=args['--with-comments'])
            else:
                save_pdf(t_id, filename=fname, with_comments=args['--with-comments'])
        if args['save_posts']:
            print('Not implemented yet')
            return

    except docopt.DocoptExit as e:
        print(e)


def test_pdf():
    h = HTML('http://habrahabr.ru/post/208802')
    h.write_pdf('habr.pdf')


def test_main():
    create_url_list('icoz', 'icoz.txt')
    pass


if __name__ == '__main__':
    # test_main()
    main()
