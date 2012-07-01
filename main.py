from views import *

app = webapp2.WSGIApplication([('/User', User),
                               ('/Undo', Undo),
                               ('/Unsubscribe', Unsubscribe),
                               ('/NewDay', NewDay),
                               ('/.*', Home)])
