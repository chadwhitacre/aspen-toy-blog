import os
import sqlite3

from aspen import Response


# Define some SQL statements.
# ===========================

CREATE = """\

CREATE TABLE IF NOT EXISTS posts
    ( year  int
    , month int
    , slug  text
    , title text
    , body  text
     );

"""

SELECT = """\

    SELECT *
      FROM posts
     WHERE year = ?
       AND month = ?
       AND slug = ?
          ;
        
"""

INSERT = """\

    INSERT
      INTO posts
           (title, body, year, month, slug) 
    VALUES (?, ?, ?, ?, ?);
        
"""

UPDATE = """\

    UPDATE posts
       SET title = ?
         , body = ?
     WHERE year = ?
       AND month = ?
       AND slug = ?
          ;
        
"""

DELETE = """\

    DELETE
      FROM posts
     WHERE year = ?
       AND month = ?
       AND slug = ?
          ;
        
"""

LIST = """\

    SELECT *
      FROM posts
  ORDER BY year, month, slug
          ;

"""


# Define a class to model a blog post.
# ====================================

class Post(dict):
    """Model a blog post.
    """

    @staticmethod
    def all():
        posts = []
        with sqlite3.Connection(dbpath) as conn:
            conn.row_factory = sqlite3.Row
            for post in conn.execute(LIST):
                posts.append(Post(post))
        return posts
   
    def get_url(self):
        out = "/%(year)s/0%(month)s/%(slug)s.html" % self
        out = out.replace('/00', '/0')
        return out

    @classmethod
    def from_path(cls, year, month, slug):

        # Validate the input.
        # ===================

        try: 
            year = int(year)
            month = int(month)
        except ValueError:
            raise Response(400)


        # Hit the database.
        # =================

        spec = (year, month, slug)
        with sqlite3.Connection(dbpath) as conn:
            conn.row_factory = sqlite3.Row
            post = conn.execute(SELECT, spec).fetchone()


        # Hydrate the object.
        # ===================

        self = cls()
        self.exists = post is not None
        if not self.exists:
            post = {'year': year, 'month': month, 'slug': slug}
        self.update(post)
        return self

    def save(self, title, body):
        """Given a title and body as strings, insert or update a db record.
        """

        # Modify the Post object itself.
        # ==============================

        self['title'] = title.strip()
        self['body'] = body.strip()


        # Modify the database.
        # ====================

        with sqlite3.Connection(dbpath) as conn:
            conn.row_factory = sqlite3.Row
            data = ( self['title']
                   , self['body']
                   , self['year']
                   , self['month']
                   , self['slug']
                    )
            if title + body == '':
                data = data[2:]
                conn.execute(DELETE, data) 
            elif self.exists:
                conn.execute(UPDATE, data)
            else:
                conn.execute(INSERT, data)

    def __getitem__(self, key):
        """Override to return empty strings for missing keys.
        """
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return ''


# Set up our database on startup.
# ===============================
# The startup function is wired up in .aspen/hooks.conf.

dbpath = None # the path to the SQLite database file

def startup(website):
    global dbpath
    dbpath = os.path.join(website.root, '.dat')
    sqlite3.Connection(dbpath).execute(CREATE)
