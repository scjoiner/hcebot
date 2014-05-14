#job in /etc/init/bots
import praw
import time
from datetime import datetime
import logging
from random import choice
import HTMLParser
import twitter
from hcetwitter import *
import config

try: #open clean logfile, TODO: archive old logfile
	logging.basicConfig(filename='/var/www/hce.txt',filemode = 'write',format='%(asctime)s %(message)s',level=logging.INFO)
except:
	logging.basicConfig(filename='log.txt', level = logging.INFO) #debug
r = praw.Reddit("gunnit mod bot")
username = config.username
password = config.password
r.login(username,password)
already_done = []
#grc_done = []
guns = r.get_subreddit('guns')
warned = []
removed = []
processed_comments = []
#grc_posters = []
print("Logged in to reddit.")
logging.info("Logged in to reddit.")
megathreads = ("Moronic Monday", "Thickheaded Thursday", "Friday Buyday", "Official Politics Thread")
ignored = ['miculekdotcom','othais','pestilence','ironchin','phteven_j','omnifox','zaptal_47','sagemassa','jedireign','shadowhce','hivbus', 'shittyimagebot','hueycobra']
moderators = ['phteven_j','ironchin','zaptal_47','shadowhce','jedireign','omnifox','sagemassa','james_johnson','hce_replacement_bot']
t = login() #try t login

banimages = []
with open("banimages.txt") as f:
	banimages = f.readlines()
for i,image in enumerate(banimages): 
	banimages[i] = banimages[i].strip('\n')

def log(message): #print and log msg
	print(message)
	logging.info(message)

def is_mod(name):
	for mod in moderators:
		if name == mod:
			return True
	return False

def replied(comment):
	replies = comment.replies
	replied = False
	for reply in replies:
		if reply.author.name == username:
			return True
	return False
	
def get_age(submission): #how old is the post
	t = datetime.now()
	utc_seconds = time.mktime(t.timetuple())
	minutes = (utc_seconds - submission.created_utc) / 60
	return minutes

def dayofweek():
	if datetime.today().weekday() == 0:
		return "Monday"
	if datetime.today().weekday() == 3:
		return "Thursday"
	if datetime.today().weekday() == 4:
		return "Friday"
	return None

def ignore_user(submission):
	username = submission.author.name
	if username.lower() in ignored:
		#print 'Found immune user: ' + username
		return True
	return False
				
def details(submission): #are details present? OR approved
	left_details = False
	submission.replace_more_comments(limit=None,threshold=0)
	comments = submission.comments
	for comment in comments:
		if comment.is_root and comment.author == submission.author:
			detailcomment = comment.body.split()
			if len(detailcomment) > 15:
				left_details = True
			break
	if ignore_user(submission) or submission.approved_by is not None:
		return True
	return left_details 

def check_replied(submission): #root reply?
	replied = False
	submission.replace_more_comments(limit=None,threshold=0)
	comments = submission.comments
	for comment in comments:
		if comment.author == r.get_redditor(username) and comment.is_root:
			replied = True
			already_done.append(submission)
			break
	return replied

def bannered(submission):
	description = guns.get_settings()["description"]
	if submission.short_link in description:
		already_done.append(submission.id)
		return True
	return False

def banner_update(submission):
	title = submission.title.lower()
	settings = guns.get_settings()
	my_str = settings[u'description']	
	my_str = HTMLParser.HTMLParser().unescape(my_str)			
	tokenized_str = my_str.split(" ")
	start_idx = 0
	new = False
	for idx, token in enumerate(tokenized_str): 
		if ('day:' in token):
			start_idx = idx
	#prevent multiple MM, etc
	if "moronic monday" in title and dayofweek() is "Monday" and "moronic monday" not in my_str.lower():
		tokenized_str[start_idx+1] = "[Moronic"
		tokenized_str[start_idx+2] = "Monday](" + submission.short_link + ")"
		new = True
	elif "thickheaded thursday" in title and dayofweek() is "Thursday" and "thickheaded thursday" not in my_str.lower():
		tokenized_str[start_idx+1] = "[Thickheaded"
		tokenized_str[start_idx+2] = "Thursday](" + submission.short_link + ")"
		new = True
	elif "friday buyday" in title and dayofweek() is "Friday" and "friday buyday" not in my_str.lower():
		tokenized_str[start_idx+1] = "[Friday"
		tokenized_str[start_idx+2] = "Buyday](" + submission.short_link + ")"
		new = True
	elif "official politics thread" in title:
		tokenized_str[start_idx+4] = "[Politics](" + submission.short_link + ")"
		new = True
	if new:
		new_description = " ".join(tokenized_str)
		guns.update_settings(description=new_description)
		bot_comment = submission.add_comment('Banner has been updated.') #post comment
		bot_comment.distinguish()
		tweet(t,"New megathread is up! %s" % submission.short_link)
		log("Updated sidebar/twitter: %s" % submission.short_link)

def is_megathread(submission):
	for keyword in megathreads:
		if keyword in submission.title and not bannered(submission):
			return True
	return False

def ban(comment):
	if replied(comment):
		return
	banitem = ""
	if comment.is_root:
		banitem = comment.submission
	else:
		parentid = comment.parent_id.partition("_")[2]
		parent =  comment.submission.permalink + parentid
		banitem = r.get_submission(parent).comments[0]
	submission = banitem
	if submission.author.name.lower() in moderators:
		return
	log("Detected ban by %s" % comment.author.name)
	guns.add_ban(submission.author)
	banimage = choice(banimages)
	try:
		reply = comment.reply(("Banned /u/%s.\n\n%s") % (submission.author.name,banimage))
		reply.distinguish()
		tweet(t,"New ban! %s" % comment.permalink)
		log("Ban succeeded. Tweet posted.")
	except:
		log("Ban failed.")

	return

def warn(comment):
	if replied(comment):
		return
	log("Detected warn by %s %s" % (comment.author.name,comment.submission.short_link))
	try:
		submission = comment.submission
		submission.remove()
		warning = submission.add_comment("Hello, /u/%s. It looks like your post violates \
										at least one of the subreddit rules and has been \
										removed. Further violations may result in a ban." \
										% submission.author.name)
		warning.distinguish()
		decrease_flair(submission)
		comment.reply("Warned /u/%s" % submission.author.name)
		#warn(submission.author)
		log("Warn succeeded.")
	except:
		log("Warn failed.")
	return

def quality(comment):
	if replied(comment):
		return
	log("Detected quality by %s" % comment.author.name)
	try:
		submission = comment.submission
		increase_flair(submission)
		comment.reply("/u/%s flair incremented." % submission.author.name)
		tweet(t,"Quality post by /u/%s! %s" % (submission.author.name,submission.short_link))
		log("Quality succeeded.")
	except Exception as e:
		log("Quality failed:" + str(e))
	return
	ranks() #update high score

def buildscore(comment):
	if replied(comment):
		return
	scoreitem = ""
	if comment.is_root:
		scoreitem = comment.submission
	else:
		parentid = comment.parent_id.partition("_")[2]
		parent =  comment.submission.permalink + parentid
		scoreitem = r.get_submission(parent).comments[0]
	user = scoreitem.author
	if user.name in moderators:
		return
	userposts = user.get_submitted(sort = 'top', time='all', limit = None)
	score = 0
	for post in userposts:
		if post.subreddit == guns and post.ups - post.downs >= 350:
			score += 1
		elif post.subreddit != guns and post.ups - post.downs <= -15:
			score -= 1
	try:
		r.set_flair(guns,user,score,"up")
		scorecomment = comment.reply("Finished scoring /u/%s. Result: %d" % (user.name,score))
		log("Scored %s: %s" % (user.name,scorecomment.permalink))
	except Exception as e:
		log("Failed to score %s: %s" % (user.name,str(e)))
		return

def check_comments():
	comments = guns.get_comments(limit = 200)
	for comment in comments:
		if comment.id not in processed_comments and comment.author is not None:
			#if comment.author.name in grc_posters: 	#remove grc comments
			#	comment.remove()
			#	print "Removed GrC comment: %s" % comment.author.name
			#	logging.info("Removed GrC comment: %s" % comment.author.name)

			if comment.author.name.lower() not in moderators:
				continue
			if "hcebot ban" in comment.body.lower():
				ban(comment)
			elif "hcebot warn" in comment.body.lower():
				warn(comment)
			elif "hcebot quality" in comment.body.lower():
				quality(comment)
			elif "hcebot score" in comment.body.lower():
				buildscore(comment)
			
			processed_comments.append(comment.id)

def increase_flair(submission):
	if submission.link_flair_css_class is not None or is_megathread(submission): #sanity check we didn't reply
		return
	user = submission.author
	flair = r.get_flair(guns,user)
	oldflair = str(flair[u'flair_text'])
	log("Increasing %s" % user.name)

	#set normaluser rank 1
	if flair is None or flair[u'flair_text'] == "0" or flair[u'flair_text'] == '':
		r.set_flair(guns,user,"1","up")
	#set poweruser rank 1
	elif oldflair is not None and oldflair.strip('-').isdigit() is False and ' | ' not in oldflair:
		new_flair = "1 | " + oldflair
		r.set_flair(guns,user,new_flair,"up")
	#increment poweruser
	elif oldflair is not None and " | " in oldflair:
		oldrank = oldflair.partition(" | ")[0]
		newrank = int(oldrank)+1
		new_flair = oldflair.replace(oldrank,str(newrank))
		r.set_flair(guns,user,new_flair,"up")
	#increment normal user
	else:
		rank = int(flair[u'flair_text']) + 1
		r.set_flair(guns,user,rank,"up")

	try:
		botcomment = submission.add_comment("Quality post detected. Incrementing flair.")
		botcomment.distinguish()
	except:
		None
	r.set_flair(guns,submission,"","quality")
	already_done.append(submission)
	return

def decrease_flair(submission):
	user = submission.author
	flair = r.get_flair(guns,user)
	if flair is None or flair[u'flair_text'] == "0" or flair[u'flair_text'] == '':
		r.set_flair(guns,user,"-1","down")
	else:
		rank = int(flair[u'flair_text'])-1
		r.set_flair(guns,user,rank,"down")
	log("Decreasing %s" % user.name)
	r.set_flair(guns,submission,"","shitpost")
	already_done.append(submission)

def check_votes(submission):
	#print submission.short_link
	if submission.author is None or submission.author.name.lower() in moderators or "miculekdotcom" in submission.author.name.lower():
		return
	karma = submission.ups - submission.downs

	replied = (submission.link_flair_css_class is not None)
	if karma > 350 and not replied and not submission.is_self: #links
		increase_flair(submission)
	elif karma > 200 and not replied and submission.is_self:   #self
		increase_flair(submission)
	elif karma < -15 and not replied:
		decrease_flair(submission)

def builduserscore(user):
	submissions = user.get_submitted(sort = 'top',time = 'all',limit = 100)
	for submission in submissions:
		if submission.subreddit == guns:
			check_votes(submission)

def remove_warning(submission):
	comments = submission.comments()
	for comment in comments:
		if comment.author.name is username and "description" in comment.body.lower():
			comment.remove()

def is_help(submission):
	helpwords = ['identif','help','recommend','can anyone','tell me','about']
	for word in helpwords:
		if word in submission.title.lower():
			already_done.append(submission.id)
			return True

def check_submissions():
	submissions = guns.get_new(limit = 50)

	#moderation
	for submission in submissions: 
		age = get_age(submission)
		if age > 60 and submission.link_flair_css_class is None:
			check_votes(submission) #look for shitpost or quality post

		#check keywords and user submission history for noob
		#if submission.is_self and submission.id not in already_done and is_noob(submission):
		#	add_faq_comment(submission)
		#	already_done.append(submission.id)

		#elif submission.id not in already_done and submission.author is not None and submission.author.name in grc_posters: #check author is not grc
		#	submission.remove()
		#	print "Removed GrC post: %s" % submission.short_link
		#	logging.info("Removed GrC post: %s" % submission.short_link)
		#	already_done.append(submission.id)

		elif submission.id not in already_done and not submission.is_self and not is_help(submission):
			
			has_details = details(submission)
			if age > 20 and submission.id and not has_details: #remove post
				log("removing " + submission.short_link)
				submission.remove()
			elif age > 10 and submission.id not in warned and not has_details and not check_replied(submission): #warn user
				print("warning " + submission.short_link + " %d minutes") % age
				log("warning " + submission.short_link)
				comment = submission.add_comment("Hello, /u/%s. Per the sidebar rules, \
												link posts require a description in the \
												comments of your post. Please add a \
												description or this post will be removed." % \
												submission.author.name)
				comment.distinguish()
				warned.append(submission.id)
			elif submission.id in warned and has_details:
				remove_warning(submission)
				already_done.append(submission.id)
				log("Unwarning %s" % submission.short_link)
			elif submission.is_self or has_details:
				already_done.append(submission.id)
	#sidebar
		elif is_megathread(submission) and submission.id not in already_done and not check_replied(submission):
			banner_update(submission)
			already_done.append(submission.id)
		elif submission.is_self:
			already_done.append(submission.id)

def main():
	#build_grc_posters()
	check_comments() 	#look for ban requests, remove grc user comments
	check_submissions()	#megathreads, sub details

while(True):
	#main() #debug
	try:
		main()
	except Exception as e:
		log(str(e))
		time.sleep(10)
