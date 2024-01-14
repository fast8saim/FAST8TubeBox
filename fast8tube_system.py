import urllib
import base64
import subprocess


def download_file(url):
    try:
        resource = urllib.request.urlopen(url)
        data = base64.b64encode(resource.read())
    except:
        data = ''

    return data


def open_browser(url, need_translate=False):
    browser = 'C:\\Users\\saim\\AppData\\Local\\Yandex\\YandexBrowser\\Application\\browser.exe' if need_translate else 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'

    subprocess.call(f'{browser} {url}')
