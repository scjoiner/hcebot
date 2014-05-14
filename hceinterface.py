from Tkinter import *
from ttk import *
import praw

r = praw.Reddit("gunnit mod bot")
username = ""
password = ""
r.login(username,password)
guns = r.get_subreddit('guns')

class hcebot:
	def __init__(self,root):

		mainframe = Frame(root, padding="0 0 0 0")
		mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
		mainframe.columnconfigure(0, weight=1)
		mainframe.rowconfigure(0, weight=1)
		loglabel = Label(mainframe,text = "Waiting...")
		loglabel.grid(column = 1, row = 6, stick = W, columnspan = 2)


		def add_flair(user,flairtext,flaircss):
			try:
				user = user.get()
				flairtext = flairtext.get()
				flaircss = flaircss.get()
				print user,flairtext,flaircss
				r.set_flair(guns,user,flairtext,flaircss)
				log("Flaired %s." % user)
			except Exception as e:
				log(str(e))

		def remove_flair(user):
			try:
				user = user.get()
				print user
				r.set_flair(guns,user,"","")
				log("Unflaired %s." % user)
			except Exception as e:
				log(str(e))

		def flair_up(user):
			flair = r.get_flair(guns,user)
			oldflair = str(flair[u'flair_text'])
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
			r.set_flair(guns,submission,"","quality")

		def flair_down(user):
			return

		def score(user):
			user = user.get()
			print "Scoring %s" % user
			user = r.get_redditor(user)
			userposts = user.get_submitted(sort = 'top', time='all', limit = None)
			score = 0
			scoreclass = None
			for post in userposts:
				if post.subreddit == guns and post.ups - post.downs >= 350:
					score += 1
				elif post.subreddit != guns and post.ups - post.downs <= -15:
					score -= -1
			if score > 1: 
				scoreclass = 'up'
			else:
				scoreclass = 'down'
			try:
				r.set_flair(guns,user,score,scoreclass)
				log("Scored %s: %d" % (user.name,score))
			except Exception as e:
				log("Failed to score %s: %s" % (user.name,str(e)))
				return

		def ban(user):
			try:
				user = user
				print user
				guns.add_ban(user)
				log("Banned %s." % user)
			except Exception as e:
				log(str(e))

		def unban(user):
			try:
				user = user
				print user
				guns.remove_ban(user)
				log("Unbanned %s." % user)
			except Exception as e:
				log(str(e))

		def log(text):
			print "Setting to %s" % text
			loglabel.config(text=text)

		def reset(fields):
			for field in fields: field.delete(0,END)
			log("Reset.")

		user = None
		flair_text = None
		flair_css = None
		user_entry = Entry(mainframe, width=10, textvariable=user)
		flair_text_entry = Entry(mainframe, width=10, textvariable=flair_text)
		flair_css_entry = Entry(mainframe, width=10, textvariable=flair_css)
		user_entry.grid(column=2, columnspan = 1,row=1, sticky="we")
		flair_text_entry.grid(column=2, columnspan = 1,row=2, sticky="we")
		flair_css_entry.grid(column=2, columnspan = 1,row=3, sticky="we")
		fields = [user_entry,flair_text_entry,flair_css_entry]

		Button(mainframe, text="Score", command=lambda:score(user_entry)).grid(column=3, row=1, sticky=W)
		Button(mainframe, text="Ban", command=lambda:ban(user_entry.get())).grid(column=3, row=2,sticky=S)
		Button(mainframe, text="Unban", command=lambda:unban(user_entry.get())).grid(column=3, row=3, sticky=S)
		Button(mainframe, text="Remove flair", command=lambda:remove_flair(user_entry)).grid(column=2, row=4, sticky=SW)
		Button(mainframe, text="Set flair", command=lambda:add_flair(user_entry,flair_text_entry,flair_css_entry)).grid(column=1, row=4, sticky=SE)
		Button(mainframe, text="Reset", command=lambda:reset(fields)).grid(column=3, row=4, sticky=SE)
		
		Label(mainframe, text="User:").grid(column=1, row=1, sticky=W)
		Label(mainframe, text="Flair text:").grid(column=1, row=2, sticky=W)
		Label(mainframe, text="Flair CSS:").grid(column=1, row=3, sticky=W)

		Separator(mainframe, orient = HORIZONTAL).grid(row=5,columnspan = 4,sticky = EW)
		Button(mainframe, text="Quit", command=root.quit).grid(column=3, row=6, sticky=SE)
		for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)
root = Tk()
root.title("Hcebot Commands")
hcebot = hcebot(root)
root.mainloop()
