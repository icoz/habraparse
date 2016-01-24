from distutils.core import setup
import habr


setup(
    name=habr.__name__,
    version=habr.__version__,
    description='Парсер для сайта habrahabr.ru',
    long_description=open('README.md').read(),
    author=habr.__author__,
    author_email='icoz.vt@gmail.com',
    url='https://github.com/icoz/habraparse',
    download_url='https://github.com/icoz/habraparse/archive/master.zip',
    py_modules=['habr'],
    maintainer='ST LEON',
    maintainer_email='leonst998@gmail.com',
    requires=['weasyprint', 'requests', 'docopt'],
    )
