import pymongo
from aspen import Response


class Post(dict):
    """Model a blog post.
    """

    @classmethod
    def from_path(cls, year, month, slug):
        try: 
            year = int(year)
            month = int(month)
        except ValueError:
            raise Response(400)

        spec = { "year": year
               , "month": month
               , "slug": slug
                }

        conn = pymongo.Connection()
        post = conn.blog.posts.find_one(spec)
        if post is None:
            post = spec
        return cls(post)

    def get_spec(self):
        return { "year": self['year']
               , "month": self['month']
               , "slug": self['slug']
                }

    def save(self, title, body):
        conn = pymongo.Connection()
        self['title'] = title
        self['body'] = body
        post = conn.blog.posts.update( self.get_spec()
                                     , {"$set": {"title": title, "body": body}}
                                     , upsert=True
                                      )

    def __getitem__(self, key):
        """Override to return empty strings for missing keys.
        """
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return ''
