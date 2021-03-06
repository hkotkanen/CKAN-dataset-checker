# encoding: utf-8
import os
import sys
from urllib2 import urlopen
import urllib2
import urlparse
import json

# From the werkzeug-project: https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/urls.py
import urllib
def url_fix(s, charset='utf-8'):
    """Sometimes you get an URL by a user that just isn't a real
    URL because it contains unsafe characters like ' ' and so on.  This
    function can fix some of the problems in a similar way browsers
    handle data entered by the user:

    >>> url_fix(u'http://de.wikipedia.org/wiki/Elf (Begriffsklärung)')
    'http://de.wikipedia.org/wiki/Elf%20%28Begriffskl%C3%A4rung%29'

    :param charset: The target charset for the URL if the url was
                    given as unicode string.
    """
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

def iterate_resources(packages):
    for package in packages:
        for resource in package['resources']:
            url = url_fix(resource['url'])
            yield dict(package=package, url=url)

def load_metadata(url):
    metadata = json.load(urlopen(url))
    packages = metadata['packages']
    return list(iterate_resources(packages))

def check_links(outfile='notfound.txt', metadata_url=None):
    if not metadata_url:
        return None

    # print "Checking for broken links from " + metadata_url
    notfound_count = 0

    resources = load_metadata(metadata_url)
    notfound = open(outfile, 'w') # just overwrite it
    for resource in resources:
        id = resource['package']['name']
        try:
            # print 'Checking broken link for ', resource['url']
            data = urlopen(resource['url'], timeout=5)

        except urllib2.HTTPError, e:
            # print >>sys.stderr, e, 'at', resource['url']
            notfound.write(e.reason + ' at ' + resource['url'] + ', from ' + resource['package']['ckan_url'] + '\n')
            notfound_count += 1
            continue

        except urllib2.URLError, e:
            # print >>sys.stderr, e, 'at', resource['url']
            notfound.write('Something went wrong at ' + resource['url'] + ', from ' + resource['package']['ckan_url'] + '\n')
            notfound_count += 1
            continue

        except Exception, e:
            # print >>sys.stderr, e, 'at', resource['url']
            notfound.write('Error: ' + e.message + ', at ' + resource['url'] + ', from ' + resource['package']['ckan_url'] + '\n')
            notfound_count += 1
            continue

    notfound.close()
    return notfound_count
