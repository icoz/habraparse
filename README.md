# habraparse
Парсер для сайта habrahabr.ru, а также для проектов Geektimes.ru и Megamozg.ru

Usage:
```
  ./habraparse.py save_favs_list [--gt|--mm] <username> <out_file>
  ./habraparse.py save_favs [--gt|--mm] [-cn --save-html --limit=N] <username> <out_dir>
  ./habraparse.py save_post [--gt|--mm] [-c --save-html] <topic_id> <out_file>
```
По умолчанию все команды работают с проектом HabraHabr.ru.
При задании опций --gt/--mm скрипт будет работать с GeekTimes.ru/Megamozg.ru

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
*01.02.2015*
- исправлены ошибки
- добавлена поддержка Geektimes.ru и Megamozg.ru
