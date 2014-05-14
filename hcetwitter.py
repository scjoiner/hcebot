import twitter

"""login to twitter with oauth"""
def login(): #return boolean if necessary?
	consumer_key = ''
	consumer_secret = ''
	oauth_token = ''
	oauth_secret = ''
	try:
		t = twitter.Api(consumer_key,consumer_secret,oauth_token,oauth_secret)
		print "Logged in to twitter."
		return t
	except Exception as e:
		print e + "Twitter login failed."

"""new tweet"""
def tweet(t,text):
	try:
		status = t.PostUpdate(text)
		print "Tweet succeeded."
	except Exception as e:
		print str(e) + "Tweet failed."

"""already tweeted?"""
def tweeted(link):
	statuses = t.GetUserTimeline(count=200,include_rts=False,exclude_replies = True)
	for status in statuses:
		if link in status.text:
			return True
	return False

"""oauth session"""
def authenticated():
	creds =  t.VerifyCredentials()

