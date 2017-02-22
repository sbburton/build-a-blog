import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **kw):
        t = jinja_env.get_template(template)
        return t.render(kw)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Blogpost(db.Model):
    title = db.StringProperty(required=True)
    blog_post = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    # https://cloud.google.com/appengine/docs/python/ndb/entity-property-reference

class MainPage(Handler):
    def renderFront(self, title="", blog_post=""):
        bps = db.GqlQuery("SELECT * FROM Blogpost "
                          "ORDER BY created DESC "
                          "LIMIT 5"
                          )
        for each in bps:
            postID = each.key().id()

        self.render("home.html", title=title, blogpost=blog_post, bps=bps, postID=postID)

    def get(self):
        self.renderFront()

    def post(self):
        self.redirect('/newpost')

class AddPost(Handler):
    def renderFront(self, title="", blog_post="", error="", postID=""):
        self.render("newpost.html", title=title, blogpost=blog_post, error=error, postID="")

    def get(self):
        self.renderFront()

    def post(self):
        title = self.request.get("title")
        blog_post = self.request.get("blog_post")

        if title and blog_post:
            bp = Blogpost(title=title, blog_post=blog_post)
            bp.put()

            postID = bp.key().id()

            self.redirect("/blog/", postID=postID)

        else:
            error = "Need to add both a Title and a Blog Post"
            self.renderFront(title=title, blog_post=blog_post, error=error)

class ViewPostHandler(Handler):
    def get(self, id):
        # self.response.write(id)


        # key = db.Key.from_path('Blogpost', int(id))
        # post = db.get(key)
        # self.rend('a_post.html', post = post)

        blog = Blogpost.get_by_id(int(id))
        # id is what you get going to port 8000
        if blog:
            self.response.write("aw yea mufucka")
        else:
            pass




app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog/', MainPage),
    ('/newpost', AddPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)

