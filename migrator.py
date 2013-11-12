import urllib

__author__ = 'florian'

from mytb import parse_trip
from mytb import parse_entry
import argparse
import yaml

# EXAMPLE TRIP: http://www.travelblog.org/Bloggers/Jack-Kerouac/Trips/22425
# EXAMPLE ENTRY: http://www.travelblog.org/Europe/Germany/Bavaria/Munich/blog-814549.html


def _verify_http_url(url):
    pieces = urllib.parse.urlparse(url)
    assert all([pieces.scheme, pieces.netloc])
    assert pieces.scheme in ['http', 'https']


def download_trip(args):
    _verify_http_url(args.trip_url)
    trip = parse_trip(args.trip_url)

    assert trip.number_entries == len(trip.entries)
    assert trip.number_photos == sum(map(lambda entry: len(entry.photos), trip.entries))

    if args.dump_html:
        for entry in trip.entries:
            args.dump_html.write('{}:\n{}\n\n\n\n'.format(entry.title, entry.text))

    print(yaml.dump(trip))


def download_entry(args):
    _verify_http_url(args.entry_url)
    entry = parse_entry(args.entry_url)

    if args.dump_html:
        args.dump_html.write('{}:\n{}\n\n\n\n'.format(entry.title, entry.text))

    print(yaml.dump(entry))


parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(dest='subparser_name')

parser_download_trip = subparsers.add_parser('download-trip', help='download a whole trip from www.mytb.org')
parser_download_trip.set_defaults(func=download_trip)
parser_download_trip.add_argument(dest='trip_url')
parser_download_trip.add_argument('--dump-html', type=argparse.FileType('w'))


parser_download_entry = subparsers.add_parser('download-entry', help='download a single entry from www.mytb.org')
parser_download_entry.set_defaults(func=download_entry)
parser_download_entry.add_argument(dest='entry_url')
parser_download_entry.add_argument('--dump-html', type=argparse.FileType('w'))


args = parser.parse_args()
args.func(args)