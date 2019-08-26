#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pprint import pprint
import sys

from weasyprint import HTML, CSS

from habr.topic import HabraTopic, PostDeleted, GeektimesTopic
from habr.user import HabraUser, GeektimesUser

__author__ = 'icoz'


def generate_comments(cmnts, id=0):
    # html_subcmnt = '''
    # <ul class="reply_comments" id="reply_comments_{c_id}">
    # {list_cmnts}
    # </ul>
    # '''
    # html_cmnt = '''
    # <li class="comment_item" id="comment_{c_id}">
    # <span class="parent_id" data-parent_id="{p_id}"></span>
    # <div class="comment_body ">
    #     <div class="info comments-list__item comment-item  " rel="{c_id}">
    #         <span class="comment-item__user-info" data-user-login="{user}">
    #         <a href="https://habrahabr.ru/users/{user}/" class="comment-item__username">{user}</a>
	# 		<time class="comment-item__time_published">{time}</time>
    #         </span>
    #         <div class="message html_format ">
    #             {cmnt_text}
    #         </div>
    #     </div>
    # </div>
    # '''
    html_cmnt = '''
        <div class="tm-comments-list__comment-wrapper">
            <div class="tm-comments-list__comment">
                <section>
                    <article class="tm-comment" style="opacity: 1; padding-left: {padding}px;"><a name="comment_{c_id}"></a>
                        <header class="tm-comment__header">
                            <div class="tm-comment-head__inner">
                                <a href="https://habr.com/ru/users/{user}/" class="tm-user-info tm-comment-head__user">
                                    <span class="tm-user-info__username">{user}</span>
                                </a>
                                <time class="tm-comment-datetime tm-comment-head__datetime">
                                    <a href="#comment_{c_id}" class="tm-comment-datetime__link">
                                        <span class="">{time}</span>
                                    </a>
                                </time>
                            </div>
                        </header>
                        <section>
                            <div class="tm-comment-body__content">
                                <div xmlns="http://www.w3.org/1999/xhtml">{cmnt_text}</div>
                            </div>
                        </section>
                    </article>
                </section>
            </div>
        </div>
    '''
    out = ''
    for c in filter(lambda x: x['p_id'] == id, cmnts):
        # print(c)
        padding = 20 if c['p_id'] == id else 0
        out += html_cmnt.format(c_id=c['c_id'], p_id=id, user=c['author'], time=c['time'], cmnt_text=c['text'], padding=padding)
        # out += html_subcmnt.format(c_id = c['c_id'], list_cmnts=generate_comments(cmnts, c['c_id']))
    return out
    # html_HEAD_cmnt.format(len_cmnts=len(cmnts), list_cmnts=out)

def prepare_html(topic, with_comments=False):
    t = topic
    # <link href="http://habrahabr.ru/styles/1412005750/printer.css" rel="stylesheet" media="print" />
    # <link href="http://habrahabr.ru/styles/1412005750/assets/global_main.css" rel="stylesheet" media="all" />
    # worked. 01/06/2016 <link href="http://habrahabr.ru/styles/1412005750/assets/post_common_css.css" rel="stylesheet" media="all" />
    #     <link href="https://habracdn.net/habr/styles/1464788371/_build/global_main.css" rel="stylesheet" media="all" />
    #     <link href="https://habracdn.net/habr/styles/1464788371/_build/company_post_show_common.css" rel="stylesheet" media="all" />
    #     <link href="https://habracdn.net/habr/styles/1464788371/_build/post_common_css.css" rel="stylesheet" media="all" />
    # 09.07.2017
    # <link href="https://habracdn.net/habr/styles/1499416660/_build/post_common_css.css" rel="stylesheet" media="all" />
    # <link href="https://habracdn.net/habr/styles/1499416660/_build/global_main.css" rel="stylesheet" media="all" />
    # <link href="https://habracdn.net/habr/styles/1499416660/_build/post_common_css.css" rel="stylesheet" media="print" />
    # <link href="https://habracdn.net/habr/styles/1499416660/_build/global_main.css" rel="stylesheet" media="print" />
    # 14.08.2018
    # <link href = "https://dr.habracdn.net/habrcom/styles/1534243008/_build/global_main.css" rel = "stylesheet" media = "all" / >
    # https://dr.habracdn.net/habrcom/styles/1534243008/stylesheets.mobile.css
    # 26/08/2019
    # https://m.habr.com/css/app.91a5df85.css
    # https://dr.habracdn.net/habrcom/styles/1566568656/main.bundle.css
    # <link href = "https://dr.habracdn.net/habrcom/styles/1566568656/main.bundle.css" rel = "stylesheet" media = "all" />

    html_head = '''
    <html>
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <meta charset="UTF-8">
    <title>{title}</title>
    <meta name="author" content="{author}">
    <meta name="generator" content="habraparse">
    <meta name="description" content="{desc}">
    <meta name="keywords" content="{keywords}">
    <meta name="viewport" content="width=device-width">
    <link href = "https://m.habr.com/css/app.91a5df85.css" rel = "stylesheet" media = "all" />
    </head>
    <body>
        <div id="app">
            <div class="tm-layout__wrapper tm-fira-loaded">
                <div class="tm-layout">
                    <div class="tm-page tm-page_narrow">
                        <div style="display:;">
                            <article class="tm-article tm-page-article__content tm-page-article__content_narrow"><!---->
                                <div class="tm-user-meta"><a class="tm-user-info" href="{author_url}">
                                    <span class="tm-user-info__username">{author}</span></a>
                                </div>
                                <h2 class="tm-article-title tm-article-title_fullview tm-article-title_fullview">
                                    <span class="tm-article-title__text">{title}</span>
                                </h2>
                                <div class="tm-tags_post"></div>
                                <div class="tm-article-body_formatted">
                                    <div class="tm-article-body">
                                        {text}
                                    </div>
                                </div>
                            </div>
                        </div>
                    
    '''
    html_cmnts = '''
    <div class="tm-page-article-comments__wrapper">
        <div class="tm-page-article-comments__title">Комментарии <span class="tm-page-article-comments__comments-count">{cmnts_count}</span></div>
        <div class="tm-page-article-comments__inner">
            <section>
                {comments}
            </section>
        </div>
    </div>
    '''
    html_foot = '''
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
    if with_comments:
        html_format = html_head + html_cmnts + html_foot
        html = html_format.format(title=t.title(), author=t.author(), author_url=t.author_url(), desc=t.desc(), text=t.text(),
                                  addstyle=t.styles(), keywords=t.keywords(),
                                  comments=generate_comments(t.comments(), 0), cmnts_count=t.comments_count())
    else:
        html_format = html_head + html_foot
        html = html_format.format(title=t.title(), author=t.author(), author_url=t.author_url(), desc=t.desc(), text=t.text(),
                                  addstyle=t.styles(), keywords=t.keywords() )
    html = str(html).replace('"//habrastorage.org', '"https://habrastorage.org')
    return html


def save_html(topic_id, filename, with_comments=False, project='h'):
    dir = os.path.dirname(filename)
    dir_imgs = filename + '.files'
    if dir != '' and not os.path.exists(dir):
        os.mkdir(dir)
    if not os.path.exists(dir_imgs):
        os.mkdir(dir_imgs)
    with open(filename, "wt") as f:
        if project == 'g':
            ht = GeektimesTopic(topic_id)
        else:
            ht = HabraTopic(topic_id)
        print('comments_cnt=', ht.comments_count())
        html = prepare_html(ht, with_comments=with_comments)
        f.write(html)
        # TODO: get all images and css
        # we need to get all links to img, css, js
        # download them to dir
        # and replace it


def save_pdf(topic_id: int, filename: str, with_comments: bool = False, project: str = 'h'):
    import logging

    logger = logging.getLogger('weasyprint')
    logger.handlers = []  # Remove the default stderr handler
    logger.addHandler(logging.FileHandler('pdf_weasyprint.log'))
    dir = os.path.dirname(filename)
    if dir != '' and not os.path.exists(dir):
        os.mkdir(dir)
    elif os.path.exists(filename):
        print("File {} is in target dir, skipping...".format(filename))
        return
    if project == 'g':
        ht = GeektimesTopic(topic_id)
    else:
        ht = HabraTopic(topic_id)

    html = prepare_html(ht, with_comments=with_comments)
    css = CSS(string='@page { size: A4; margin: 1cm; !important;} img { width: 100%; height: auto; !important; }')
    #css = CSS(string='@page { size: A4 landscape; margin: 1cm !important}')
    HTML(string=html).write_pdf(filename, stylesheets=[css])


def save_all_favs_for_user(username, out_dir, save_in_html=True, with_comments=False, save_by_name=False, limit=None,
                           project='h'):
    filetype = 'pdf'
    if save_in_html:
        filetype = 'html'
    if project == 'g':
        hu = GeektimesUser(username, need_favorites=True)
    else:
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
        print('Downloading "{}" ({})...'.format(topic_name, topic_id))
        if save_by_name:
            t_name = topic_name.replace('/', '_').replace('\\', '_').replace('!', '.').replace(':', '.').replace(';',
                                                                                                                 '.')
            if len(t_name) > 250:
                t_name = t_name[:250]
            filename = '{dir}/{name}.{filetype}'.format(dir=out_dir, name=t_name, filetype=filetype)
        else:
            filename = '{dir}/{id}.{filetype}'.format(dir=out_dir, id=topic_id, filetype=filetype)
        print('Saving it in "{}"'.format(filename))
        try:
            if save_in_html:
                save_html(topic_id, filename, with_comments=with_comments, project=project)
            else:
                save_pdf(topic_id, filename, with_comments=with_comments, project=project)
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


def create_url_list(username, filename, project='h'):
    '''
    Generates url list for favorites
    :param username:
    :param filename:
    :param project: one of 'h', 'g'
    :return:
    '''
    hu = GeektimesUser(username) if project == 'g' else HabraUser(username)
    T = GeektimesTopic if project == 'g' else HabraTopic
    urls = list()
    favs_id = hu.favorites()
    if favs_id:
        for topic_name in favs_id:
            try:
                urls.append(T(favs_id[topic_name]).getTopicUrl())
            except PostDeleted:
                print('Post {} is deleted!'.format(favs_id[topic_name]))
        urls.sort()
        with open(filename, 'wt') as f:
            f.write('\n'.join(urls))
    else:
        print("Something went wrong. Maybe user is banned or deleted.")


import docopt


def main():
    # {prog} save_posts [--gt|--mm] [-c --save-html --limit=N] <username> <out_dir>
    params = """Usage:
        {prog} save_favs_list [--gt] <username> <out_file>
        {prog} save_favs [--gt] [-cn --save-html --limit=N] <username> <out_dir>
        {prog} save_post [--gt] [-c --save-html] <topic_id> <out_file>
        {prog} --help

    Arguments:
        username  Имя пользовтеля Habrahabr.ru | Geektimes.ru | Megamozg.ru
        out_file  Имя файла для сохранения списка избранного пользователя username
        out_dir   Путь для сохранения избранного

    Options:
        --gt                Работать с Geektimes
        -c, --with-comments     Сохранить вместе с коментариями
        --save-html          Сохранить в HTML (по умолчанию, в PDF)
        -n, --save-by-name       Сохранять с именем, полученным из названия статьи (по умолчанию - по ID статьи)
        --limit=N          Ограничить количество в N статей
    """.format(prog=sys.argv[0])

    try:
        args = docopt.docopt(params)
        project = 'g' if args.get('--gt') else 'h'
        if args['save_favs_list']:
            create_url_list(args['<username>'], args['<out_file>'], project=project)
            return
        if args['save_favs']:
            save_all_favs_for_user(args['<username>'], args['<out_dir>'], save_in_html=args['--save-html'],
                                   with_comments=args.get('--with-comments', False),
                                   save_by_name=args['--save-by-name'],
                                   limit=args['--limit'], project=project)
            return
        if args['save_post']:
            t_id = args['<topic_id>']
            fname = args['<out_file>']
            if args['--save-html']:
                save_html(t_id, filename=fname, with_comments=args.get('--with-comments', False), project=project)
            else:
                save_pdf(t_id, filename=fname, with_comments=args.get('--with-comments', False), project=project)

    except docopt.DocoptExit as e:
        print(e)


if __name__ == '__main__':
    main()
