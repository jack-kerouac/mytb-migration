import logging
import logging.config
import os
import urllib
import argparse

import requests
import yaml

from mytb import parse_trip
from mytb import parse_entry
from wordpress import WordpressSite


# EXAMPLE TRIP: http://www.travelblog.org/Bloggers/Jack-Kerouac/Trips/22425
# EXAMPLE ENTRY: http://www.travelblog.org/Europe/Germany/Bavaria/Munich/blog-814549.html


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARN)
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'INFO',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        'mytb': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        'migrator': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
    }
})


def _store_entry(entry, entry_dir, separate_text_file=True, download_photos=True):
    os.mkdir(entry_dir)

    # ENTRY TEXT
    if separate_text_file:
        with open(os.path.join(entry_dir, 'text.html'), mode='tw', encoding='utf-8') as content_file:
            content_file.write(entry.text)
        del entry.text

    # PHOTOS
    # put photos in the entry folder, not a sub folder
    photo_dir = entry_dir
    if download_photos:
        for i, photo in enumerate(entry.photos):
            # referer header required, otherwise: 403 - Hotlinking is forbidden
            logging.info('downloading photo from %s', photo.mytb_url)
            r = requests.get(photo.mytb_url, headers={'referer': entry.mytb_url})
            photo_path = os.path.join(photo_dir, "{0:03d}.jpg".format(i))
            photo.local_path = os.path.relpath(photo_path, start=entry_dir)
            with open(photo_path, mode='bw') as photo_file:
                photo_file.write(r.content)

    # ENTRY METADATA
    # write after the rest, since entries are modified (local path is added to photos, ...)
    with open(os.path.join(entry_dir, 'entry.yaml'), mode='tw', encoding='utf-8') as entry_file:
        yaml.dump(entry, entry_file)


def _store_trip(trip, trip_dir, separate_text_file=True, download_photos=True):
    os.mkdir(trip_dir)

    # ENTRIES
    for i, entry in enumerate(trip.entries):
        entry_dir = os.path.join(trip_dir, '{0:03d}'.format(i))
        _store_entry(entry, entry_dir, separate_text_file=separate_text_file, download_photos=download_photos)

    del trip.entries

    # TRIP METADATA
    # write after the rest, since entries are modified (local path is added to photos, ...)
    with open(os.path.join(trip_dir, 'trip.yaml'), mode='tw', encoding='utf-8') as trip_file:
        yaml.dump(trip, trip_file)



def _verify_http_url(url):
    pieces = urllib.parse.urlparse(url)
    assert all([pieces.scheme, pieces.netloc])
    assert pieces.scheme in ['http', 'https']


def download_trip(args):
    _verify_http_url(args.trip_url)
    trip = parse_trip(args.trip_url)

    assert trip.number_entries == len(trip.entries)
    assert trip.number_photos == sum(map(lambda entry: len(entry.photos), trip.entries))

    target_dir = os.path.abspath(args.target_directory)
    _store_trip(trip, target_dir)


def download_entry(args):
    _verify_http_url(args.entry_url)
    entry = parse_entry(args.entry_url)

    target_dir = os.path.abspath(args.target_directory)
    _store_entry(entry, target_dir)


def wp_access_token(args):
    access_token = WordpressSite.obtain_access_token(args.client_id, args.client_secret, args.redirect_uri)
    print(access_token)


parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(dest='subparser_name', title='subcommands')

parser_download_trip = subparsers.add_parser('download-trip', help='download a whole trip from www.mytb.org')
parser_download_trip.set_defaults(func=download_trip)
parser_download_trip.add_argument(dest='trip_url')
parser_download_trip.add_argument('-t', '--target-directory', help='will be created', required=True)


parser_download_entry = subparsers.add_parser('download-entry', help='download a single entry from www.mytb.org')
parser_download_entry.set_defaults(func=download_entry)
parser_download_entry.add_argument(dest='entry_url')
parser_download_entry.add_argument('-t', '--target-directory', help='will be created', required=True)


parser_wp_access_token = subparsers.add_parser('wp-access-token', help='retrieve the access token for a wordpress blog')
parser_wp_access_token.set_defaults(func=wp_access_token)
parser_wp_access_token.add_argument('--client-id', required=True)
parser_wp_access_token.add_argument('--client-secret', required=True)
parser_wp_access_token.add_argument('--redirect-uri', required=True)



args = parser.parse_args()
if hasattr(args, 'func'):
    args.func(args)
else:
    parser.print_usage()