import urllib
import base64


def download_file(url):
    resource = urllib.request.urlopen(url)
    return base64.b64encode(resource.read())
