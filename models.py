from google.appengine.ext import db
from google.appengine.api import mail
from datetime import date, timedelta

class UserInfo(db.Model):
  email = db.EmailProperty(required=True)
  minutes = db.IntegerProperty(default=0)
  exercisetoday = db.BooleanProperty(default=False)
  minutestoday = db.IntegerProperty(default=0)
  rewarder = db.EmailProperty(required=True)
  subscibed = db.BooleanProperty(default=True)
  rewards = db.StringListProperty(default=[])
  prices = db.ListProperty(int,default=[])

  def AddMinutes(self,numminutes,today=True):
    self.minutes += numminutes
    if today: self.minutestoday += numminutes
    self.put()

  def Exercise(self,status):
    self.exercisetoday = status
    self.put()

  def Email(self,email):
    self.email = email
    self.put()

  def Rewarder(self,rewarder):
    self.rewarder = rewarder
    self.put()

  def Reward(self,data):
    if data[0]=='__delete__':
      self.rewards.pop(int(data[1]))
      self.prices.pop(int(data[1]))
    else:
      self.rewards.append(data[0])
      self.prices.append(int(data[1]))
    self.put()

  def Unsubscribe(self,rewarder):
    self.subscribed = False
    self.put()

  def NewDay(self):
    if not self.exercisetoday:
      self.minutes -= 300
      self.ExerciseEmail()
    self.minutestoday = 0
    self.exercisetoday = False
    self.put()

  def ExerciseEmail(self):
    message = mail.EmailMessage()
    message.sender = 'Credit Tracker <webmaster@tyrannosaurusprep.com>'
    message.to = self.email
    message.subject = "Exercise Penalty"
    message.body = """
You have been penalized 6 credits for failing to exercise on %s. If this is incorrect, go to http://credit.tyrannosaurusprep.com/Undo?userid=%s to regain your credits. If you would like to stop receiving these email alerts, go to http://credit.tyrannosaurusprep.com/Unsubscribe?userid=%s.


Best Regards,
Credit Tracker
    """ % (date.today()-timedelta(1), self.key().name(), self.key().name())
    message.send()
