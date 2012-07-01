import webapp2
from google.appengine.api import users
from django.template import Context, loader
from django.conf import settings
import random
from models import *
from datetime import tzinfo, timedelta, datetime

settings.configure( TEMPLATE_DIRS = ['templates'] )
congratulations = ['Way to go!','Well done!','Oh yeah!','Great work!','Excellent!','Very cool!','Yay!','Fantastic!']

DSTSTART = datetime(1, 4, 1, 2)
DSTEND = datetime(1, 10, 25, 1)

def first_sunday_on_or_after(dt):
  days_to_go = 6 - dt.weekday()
  if days_to_go:
    dt += timedelta(days_to_go)
  return dt

class EDT(tzinfo):
  def utcoffset(self, dt):
    return timedelta(hours=-5) + self.dst(dt)
  def dst(self, dt):
    start = first_sunday_on_or_after(DSTSTART.replace(year=dt.year))
    end = first_sunday_on_or_after(DSTEND.replace(year=dt.year))
    if start <= dt.replace(tzinfo=None) < end:
      return timedelta(hours=1)
    else:
      return timedelta(0)

def UserContext():
  user = users.get_current_user()
  userinfo = UserInfo.get_by_key_name(user.user_id())
  if not userinfo:
    userinfo = UserInfo(key_name=user.user_id(),email=user.email().lower(),rewarder=user.email().lower())
    userinfo.put()
  rewards = zip(userinfo.rewards, userinfo.prices)
  return Context({ 'userinfo': userinfo, 'rewards': rewards, 'userid': user.user_id(), 'date': datetime.now(EDT()) })

def Change(userinfo,request):
  field = request.get('field')
  data = request.get('data')
  if field == 'minutes':
    userinfo.AddMinutes(int(data))
    return("%s %s minutes added!" % (random.choice(congratulations), data))
  if field == 'exercise':
    userinfo.Exercise(data=='true')
    if data == 'true':
      return("%s You exercised today!" % random.choice(congratulations))
    return("Not exercised yet.")
  if field == 'email':
    userinfo.Email(data)
    return("Email address changed to %s." % data)
  if field == 'rewarder':
    userinfo.Rewarder(data)
    return("Rewarder changed to %s." % data)
  if field == 'reward':
    data = data.split('__s__')
    userinfo.Reward(data)
    if data[0] == '__delete__':
      return('Item deleted.')
    else:
      return('"%s" added.' % data[0])

def Purchase(userinfo,request):
  cost = int(request.get('cost'))
  userinfo.AddMinutes(-cost,False)
  if request.get('title')=='__donate__':
    db.GqlQuery("SELECT * FROM UserInfo WHERE email = '%s'" % userinfo.rewarder.lower()).get().AddMinutes(cost,False)
    return("Donated %s credits to %s." % (cost/60, userinfo.rewarder))
  message = mail.EmailMessage()
  message.sender = 'Credit Tracker Rewards <webmaster@tyrannosaurusprep.com>'
  message.to = userinfo.rewarder
  message.subject = "Reward Purchased"
  message.body = """
%s has purchased %s for %s credits.


Best Regards,
Credit Tracker
  """ % (userinfo.nickname, request.get('title'), cost/60)
  message.send()
  return("Purchased %s for %s credits." % (request.get('title'), cost/60))

class User(webapp2.RequestHandler):
  def get(self):
    if not users.get_current_user():
      self.redirect(users.create_login_url(self.request.uri))
    else:
      self.response.out.write(loader.get_template('user.html').render(UserContext()))
  def post(self):
    userinfo = UserInfo.get_by_key_name(self.request.get('userid'))
    self.response.out.write(Purchase(userinfo,self.request))
  def put(self):
    userinfo = UserInfo.get_by_key_name(self.request.get('userid'))
    self.response.out.write(Change(userinfo,self.request))
  def delete(self):
    userinfo = UserInfo.get_by_key_name(self.request.get('userid'))
    userinfo.delete()
    self.response.out.write('Account deleted.')

class Undo(webapp2.RequestHandler):
  def get(self):
    userinfo = UserInfo.get_by_key_name(self.request.get('userid'))
    userinfo.AddMinutes(300,False)
    self.redirect('/User')

class Unsubscribe(webapp2.RequestHandler):
  def get(self):
    userinfo = UserInfo.get_by_key_name(self.request.get('userid'))
    userinfo.Unsubscribe()
    self.redirect('/User')

class NewDay(webapp2.RequestHandler):
  def get(self):
    userinfos = UserInfo.all()
    for userinfo in userinfos:
      userinfo.NewDay()

class Home(webapp2.RequestHandler):
  def get(self):
    if users.get_current_user() and not self.request.get('about')=='t':
      self.redirect('/User')
    else:
      self.response.out.write(loader.get_template('base.html').render(Context({})))
