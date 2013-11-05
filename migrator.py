import logging

__author__ = 'florian'

from pyquery import PyQuery
import blog
import dateutil.parser as dparser
import lxml


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def has_class(element, class_):
    if not PyQuery(element).attr.class_:
        return False
    else:
        return class_ in PyQuery(element).attr.class_.split(' ')


def is_text(node):
    return type(node) == lxml.etree._ElementUnicodeResult


def get_text_nodes(pyquery):
    return filter(lambda node: is_text(node), pyquery.contents())


def is_element(node, tag=None):
    if is_text(node):
        return False

    if tag:
        return node.tag == tag
    else:
        return True




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

    # remove <br> before and after <h2>
    c('h2').prev('br').remove()
    c('h2').next('br').remove()

    # remove <br>s after <h2>
    c('h2 + br').remove()
    c('h2 + br').remove()

    # remove last <br>
    c('br.clear').remove()

    # remove last <hr>
    c('hr.divider_hr').remove()

    # replace div.quote_wrapper by blockquotes
    for quote in c('div.quote_wrapper').items():
        quote.replaceWith('<blockquote>{}</blockquote>'.format(quote.text()))

    # properly format lists
    for list_ in c('ul, ol').items():
        text_nodes = get_text_nodes(list_)
        list_.html(''.join(['<li>' + item.replace(' • ', '') + '</li>' for item in text_nodes]))

    # WORKING ON THE CONTENT AS STRING FROM HERE ON

    # replace strange \r returned by mytb and remove leading and trailing whitespace
    content.html(content.html().replace('&#13;', '').strip())

    # replace double <br>s with <p>s
    if c('p'):
        logger.warn('there is a <p> tag in content: %s', content.html(pretty_print=True))

    text = content.html().strip()
    text = text.replace('<br/><br/>', '</p><p>')
    text = '<p>' + text + '</p>'

    content.html(text)
    entry.text = content.html(pretty_print=True)

    pass


def parse_photos(entry, html):
    c = html.find

    # first page
    for photo_blog in c('.photo_blog').items():
        photo = blog.Photo()
        photo.url = photo_blog.find('img:first').attr('data-src')
        photo.title = photo_blog.find('img:first').attr('title')
        photo.subtitle = PyQuery(photo_blog.contents()[-1]).text() if photo_blog.find('hr') else ''

        entry.photos.append(photo)

    # more photos on other pages?
    # TODO: add more photos
    if c('.breadcrumbs nav_wrapper').children():
        pass


def parse_entry(url):
    logger.info('Reading mytb entry from {}'.format(url))

    entry = blog.Entry()
    entry.mytb_url = url

    d = PyQuery(url, parser='html')

    parse_meta(entry, d.clone())

    parse_text(entry, d.clone())

    parse_photos(entry, d.clone())

    return entry


def parse_trip(url):
    trip = blog.Trip()
    trip.mytb_url = url

    content = PyQuery(url, parser='html')('#content')
    text_nodes = list(get_text_nodes(content))

    trip.title = str(text_nodes[2])

    trip.from_ = dparser.parse(content.find('.info .date').eq(0).text())
    trip.until = dparser.parse(content.find('.info .date').eq(1).text())

    trip.number_entries = int(text_nodes[4])
    trip.number_photos = int(text_nodes[5])

    content.make_links_absolute()
    urls = map(lambda tr: tr('a').attr('href'), content.find('table tr').items())

    trip.entries = [parse_entry(url) for url in urls]

    return trip


# TEST entry
#e = parse_entry('http://www.travelblog.org/Europe/Germany/Bavaria/Munich/blog-814549.html')
#print(e.text)


trip = parse_trip('http://www.travelblog.org/Bloggers/Jack-Kerouac/Trips/22425')

for entry in trip.entries:
    print('{}:\n{}\n\n\n\n'.format(entry.title, entry.text))

assert trip.number_entries == len(trip.entries)
# TODO: reenable this assertion as soon as all photos are parsed
#assert trip.number_photos == sum(map(lambda entry: len(entry.photos), trip.entries))
