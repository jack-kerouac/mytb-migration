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

    #for entry in trip.entries:
    #    print('{}:\n{}\n\n\n\n'.format(entry.title, entry.text))

    assert trip.number_entries == len(trip.entries)
    assert trip.number_photos == sum(map(lambda entry: len(entry.photos), trip.entries))

    print(yaml.dump(trip))


def download_entry(args):
    _verify_http_url(args.entry_url)
    entry = parse_entry(args.entry_url)

    print(yaml.dump(entry))


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='subparser_name')

parser_prepare = subparsers.add_parser('download-trip', help='download a whole trip from www.mytb.org')
parser_prepare.set_defaults(func=download_trip)
parser_prepare.add_argument(dest='trip_url')

parser_prepare = subparsers.add_parser('download-entry', help='download a single entry from www.mytb.org')
parser_prepare.set_defaults(func=download_entry)
parser_prepare.add_argument(dest='entry_url')

args = parser.parse_args()
args.func(args)