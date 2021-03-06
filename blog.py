class Travelblog:
    """Represents a whole travel blog with a set of trips"""

    def __init__(self, blogger, trips):
        self.blogger = blogger
        self.trips = trips


class Trip:
    """Represents one trip with a set of entries

    - mytb URL
    - title
    - description
    - from_
    - until
    - #blog entries
    - #photos

    - entries (list)
    """


class Entry:
    """
    An entry

    - mytb URL
    - title
    - location (list)
    - date
    - publish date
    - text
    - photos (list)
    - comments
    - # views
    """

    def __str__(self):
        return "{}: {}".format(self.title, self.location)


class Comment:
    """
    A comment

    - date
    - author
    - title
    - text
    """


class Photo:
    """
    A photo

    - URL
    - title
    - subtitle
    """