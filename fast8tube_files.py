import urllib


def download_file(name, url):
    resource = urllib.request.urlopen(url)
    out = open(name, 'wb')
    out.write(resource.read())
    out.close()
