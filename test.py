from lxml import html
from xml.sax import saxutils
import requests

cardset = 'xln'
cardcode = 217
url = 'https://tagger.scryfall.com/card/' + cardset + '/' + str(cardcode)
print(url)

page = requests.get(url)
pagetree = html.fromstring(page.content)


def inner_html(tree):
    """ Return inner HTML of lxml element """
    return (saxutils.escape(tree.text) if tree.text else '') + \
        ''.join([html.tostring(child, encoding=str) for child in tree.iterchildren()])


print(inner_html(pagetree))
