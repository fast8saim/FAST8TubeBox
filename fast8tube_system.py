import urllib
import base64
import subprocess


def download_file(url):
    resource = urllib.request.urlopen(url)
    return base64.b64encode(resource.read())


def open_browser(url, need_translate=False):
    browser = 'C:\\Users\\saim\\AppData\\Local\\Yandex\\YandexBrowser\\Application\\browser.exe' if need_translate else 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'

    subprocess.call(f'{browser} {url}')
