# tropy.py - "Tropy" in Python for Google App Engine.
# Copyright (C) 2005,2006,2009 by Hiroshi Yuki.
# http://www.hyuki.com/tropy/
# http://tropy-page.appspot.com/
#
# This program is free software; you can redistribute it and/or
# modify it under the same terms as Perl itself.
#
import random
import os
import cgi
import re
import hashlib

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Tropypage(db.Model):
  pageid = db.StringProperty()
  caption = db.StringProperty()
  content = db.StringProperty(multiline=True)

class TopPage(webapp.RequestHandler):
  def get(self):
    m = re.match('^(\d\d\d\d\d\d\d\d)$', self.request.query_string)
    if m:
      self.showPage(m.group(1))
    else:
      self.showRandomPage()

  def showPage(self, pageid):
    page = Tropypage.get_by_key_name('key' + pageid)
    if page is None:
      self.redirect('/')
      return
    if page.caption is None: page.caption = ''
    if page.content is None: page.content = ''
    page.caption = cgi.escape(page.caption)
    page.content = re.sub(r'\r?\n', '\n', page.content)
    page.content = cgi.escape(re.sub(r'\n\n(\n)+', '\n\n', page.content))
    page.content = '<p>' + re.sub(r'\n\n', '</p><p>', page.content) + '</p>'
    # Background color
    m = hashlib.md5(pageid).hexdigest()
    r = 255 - int(m[0:2], 16) % 32
    g = 255 - int(m[2:4], 16) % 32
    b = 255 - int(m[4:6], 16) % 32
    bgcolor = "#%02X%02X%02X" % (r, g, b)
    color = 'black'
    self.response.out.write(template.render(os.path.join(os.path.dirname(__file__), 'top.html'),
      {
        'pageid': pageid,
        'caption': page.caption,
        'content': page.content,
        'url': self.request.url,
        'color': color,
        'bgcolor': bgcolor,
      }))

  def showRandomPage(self):
    query = Tropypage.all()
    count = query.count()
    if count == 0:
      self.redirect('/c')
      return
    offset = random.randint(0, count - 1)
    pages = query.fetch(1, offset=offset)
    pageid = pages[0].pageid
    if pageid is None:
      self.redirect('/')
      return
    host = self.request.headers['Host']
    absolute_url = 'http://' + host + '/?' + pageid
    self.response.out.write(template.render(os.path.join(os.path.dirname(__file__), 'jump.html'),
      {
        'absolute_url': absolute_url,
      }))

class EditPage(webapp.RequestHandler):
  def get(self):
    m = re.match('^(\d\d\d\d\d\d\d\d)$', self.request.query_string)
    if not m:
      self.redirect('/')
      return
    pageid = m.group(1)
    page = Tropypage.get_by_key_name('key' + pageid)
    if page is None:
      self.redirect('/')
      return
    if page.caption is None: page.caption = ''
    if page.content is None: page.content = ''
    self.response.out.write(template.render(os.path.join(os.path.dirname(__file__), 'edit.html'),
      {
        'pageid': pageid,
        'caption': page.caption,
        'content': page.content,
        'url': self.request.url,
      }))

class CreatePage(webapp.RequestHandler):
  def get(self):
    pageid = '%08d' % random.randint(1, 100000000)
    self.response.out.write(template.render(os.path.join(os.path.dirname(__file__), 'create.html'),
      {
        'pageid': pageid,
        'caption': 'New Page',
        'content': '',
      }))

class WritePage(webapp.RequestHandler):
  def post(self):
    pageid = self.request.get('pageid')
    m = re.match('^(\d\d\d\d\d\d\d\d)$', pageid)
    if not m:
      self.redirect('/')
      return
    caption_content = self.request.get('caption_content')
    caption_content = caption_content[:500]
    lines = caption_content.split("\n")
    caption = lines.pop(0).rstrip("\r")
    content = "\n".join(lines)
    page = Tropypage.get_or_insert('key' + pageid)
    page.pageid = pageid
    page.caption = caption
    page.content = content
    page.put()
    self.redirect('/?' + pageid)

application = webapp.WSGIApplication([
  ('/e', EditPage),
  ('/c', CreatePage),
  ('/w', WritePage),
  ('/', TopPage),
  ], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
