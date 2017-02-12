# habraparse
[![Build Status](https://travis-ci.org/icoz/habraparse.svg?branch=master)](https://travis-ci.org/icoz/habraparse)
[![Code Climate](https://codeclimate.com/github/icoz/habraparse/badges/gpa.svg)](https://codeclimate.com/github/icoz/habraparse)
[![Issue Count](https://codeclimate.com/github/icoz/habraparse/badges/issue_count.svg)](https://codeclimate.com/github/icoz/habraparse)

Парсер для проектов Habrahabr.ru и Geektimes.ru 

Для работы скрипта необходимо установить зависимости
```
pip install -r requirements.txt
```


Usage:
```
  ./habraparse.py save_favs_list [--gt] <username> <out_file>
  ./habraparse.py save_favs [--gt] [-cn --save-html --limit=N] <username> <out_dir>
  ./habraparse.py save_post [--gt] [-c --save-html] <topic_id> <out_file>
```
По умолчанию все команды работают с проектом HabraHabr.ru.
При задании опции --gt скрипт будет работать с GeekTimes.ru

Команды:
```
  save_favs_list - сохранение в файл <out_file> списка URL избранного для пользователя <username>
  save_favs - сохранение в папку <out_dir> статей из избранного для пользователя <username>
  save_post - сохранение в файл <out_file> стати с заданным ID
```

Описание опций:
```
  --save-html          Сохранить в HTML (по умолчанию, в PDF)
  -n, --save-by-name       Сохранять с именем, полученным из названия статьи (по умолчанию - по ID статьи)
  -c, --with-comments     Сохранить вместе с коментариями
  --limit=N          Ограничить количество в N статей
```

Changelog:
*12.02.2017*
- Добавлены мета теги для лучшего поиска PDF
- Исправлена вставка автора(вставляется ссылка на автора рабочая)
- Решана проблема с маштабированием изображений
- Теперь тестируется только python 3.5 и 3.6, на других версиях тоже может работать.

*01.02.2015*
- исправлены ошибки
- добавлена поддержка Geektimes.ru и Megamozg.ru
*28.05.2016*
- удалена поддержка Megamozg в связи с его кончиной (R.I.P.)
*11.12.2016*
- исправлено поведение согласно изменениям на сайте
- добавлен файл requirements.txt

Распространяется по лицензии GNU GPL v2.0.
Under license GNU GPL v2.0
