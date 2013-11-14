import logging
import urllib
import re

from pyquery import PyQuery
import dateutil.parser as dparser
import lxml

import blog


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BASE_URL = 'http://www.travelblog.org'


def pyquery(url):
    return PyQuery(url,
                   opener=lambda u, **kw: urllib.request.urlopen(u).read().decode('utf-8'),
                   parser='html')


def is_text(node):
    return type(node) == lxml.etree._ElementUnicodeResult


def get_text_nodes(pyquery):
    return [str(node) for node in filter(lambda node: is_text(node), pyquery.contents())]


def parse_meta(entry, body):
    # title
    entry.title = body.find('div.blog_header h1').text()

    # location
    entry.location = [x.text for x in (list(body.find('div.blog_header a')))]
    entry.location.reverse()

    # date
    entry.date = dparser.parse(body.find('span.blog_date').text())

    # publish date
    entry.publish_date = dparser.parse(body.find('span.blog_date_published').text().replace('Published: ', ''))


def parse_text(entry, body):
    content = body.find('div.blog_content')
    c = content.find

    # WORKING ON THE CONTENT USING PYQUERY FROM HERE ON
    # remove unnecessary content
    c('.ads_leader').remove()
    c('.blog_info + hr').remove()
    c('.blog_info').remove()
    c('.photo_blog').remove()
    c('.blognav').remove()
    c('.clean_head').remove()

    # remove one of the two <br>s after <h2>
    c('h2 + br').remove()

    # remove last <br>
    c('br.clear').remove()

    # remove last <hr>
    c('hr.divider_hr').remove()

    # replace div.quote_wrapper by <q>
    for quote in c('div.quote_wrapper').items():
        quote.replaceWith('<q>{}</q>'.format(quote.text()))

    # properly format lists
    for list_ in c('ul, ol').items():
        text_nodes = get_text_nodes(list_)
        list_.html(''.join(['<li>' + item.replace(' • ', '') + '</li>' for item in text_nodes]))

    # WORKING ON THE CONTENT AS STRING FROM HERE ON   (FUNKY!)

    # replace strange \r returned by mytb and remove leading and trailing whitespace
    content.html(content.html().replace('&#13;', '').strip())

    # replace double <br>s with <p>s
    if c('p'):
        logger.warn('there is a <p> tag in content: %s', content.html(pretty_print=True))

    text = content.html().strip()
    text = re.sub(r'<br/>\s*<br/>', '</p><p>', text)
    text = '<p>' + text + '</p>'

    text = re.sub(r'<br/>\s*<h2>', '</p><h2>', text)
    text = re.sub(r'</h2>\s*<br/>', '</h2><p>', text)

    # parse and pretty print it
    content.html(text)
    entry.text = content.html(pretty_print=True)

    pass


def full_photo_from_thumbnail(thumbnail_photo_url):
    # this is not really solid. If mytb changes URL paths, this will not work anymore!
    return thumbnail_photo_url.replace('/t/', '/f/')


def get_photos_on_page(html):
    photos = []

    for photo_blog in html('.photo_blog').items():
        photo = blog.Photo()
        # since the link inside the entry page is to the thumbnail version of the image, transform it to the full URL
        photo.mytb_url = full_photo_from_thumbnail(photo_blog.find('img:first').attr('data-src'))
        photo.title = photo_blog.find('img:first').attr('title')
        photo.subtitle = PyQuery(photo_blog.contents()[-1]).text() if photo_blog.find('hr') else ''

        photos.append(photo)

    return photos


def parse_photos(entry, html):
    entry.photos = []

    # first page
    entry.photos.extend(get_photos_on_page(html))

    # more photos on other pages?
    more_photo_nav = html('.breadcrumbs .nav_wrapper')
    if more_photo_nav.children():
        more_photo_nav.make_links_absolute(BASE_URL)
        additional_photo_pages = [a.attr('href') for a in list(more_photo_nav('a').items())[:-1]]
        for url in additional_photo_pages:
            logger.info('reading another photo page')
            html = pyquery(url)
            entry.photos.extend(get_photos_on_page(html))


def parse_comment(entry, html):
    comments = html('div.comment_display')

    entry.comments = []

    for comment_elem in comments.items():
        comment = blog.Comment()

        text_nodes = get_text_nodes(comment_elem)

        comment.date = dparser.parse(text_nodes[0].strip().replace('Date: ', ''))
        comment.author = get_text_nodes(comment_elem('.from a'))[0].strip()

        comment.title = comment_elem('b').text()
        comment.text = text_nodes[2].strip()

        entry.comments.append(comment)

    pass


def parse_entry(url):
    logger.info('Reading mytb entry from {}'.format(url))

    entry = blog.Entry()
    entry.mytb_url = url

    d = pyquery(url)

    parse_meta(entry, d.clone())

    parse_text(entry, d.clone())

    parse_photos(entry, d.clone())

    parse_comment(entry, d.clone())

    return entry


def parse_trip(url):
    trip = blog.Trip()
    trip.mytb_url = url

    content = pyquery(url)('#content')
    text_nodes = get_text_nodes(content)

    trip.title = content('h1').text()
    trip.description = str(text_nodes[2])

    trip.from_ = dparser.parse(content.find('.info .date').eq(0).text())
    trip.until = dparser.parse(content.find('.info .date').eq(1).text())

    trip.number_entries = int(text_nodes[4])
    trip.number_photos = int(text_nodes[5])

    content.make_links_absolute(BASE_URL)
    urls = map(lambda tr: tr('a').attr('href'), content.find('table tr').items())

    trip.entries = [parse_entry(url) for url in urls]

    return trip