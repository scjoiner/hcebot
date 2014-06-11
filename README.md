hcebot
======

/r/guns /u/hce_replacement_bot moderation automation

Summary:
* Automated post removal if no description added
* Flair system (increment/decrement auto or manual)
* Automated banner megathread link updates
* Triggers for bans, warnings, flairs by mods
* Integrates with twitter (@hcebot) for subreddit highlights
* Optional GUI for quick functions
* Logs to stdout and logfile for debug

TODO:
* Archive logs

Commands: Prefixed with "hcebot" to draw the bots attention. Command is given one space after, e.g. "hcebot COMMAND". Case agnostic.
* Ban: Bans user indefinitely, leaves comment with ban image
* Warn: Removes post, leaves warning comment, decreases user flair
* Quality: Marks post as quality post, increases user flair, leaves comment
* Buildscore: Scores user's previous submissions and edits flair to match
* Remove kebab: Same as ban, requested by /u/Omnifox

Automated features:
* Scans for megathreads [Moronic Monday, Thickheaded Thursday, Friday Buyday, Official Politics Thread], updates banner if day of week is correct and no thread exists for the current megathread
* Auto-increments user flair if post karma is above link/self threshold
* Auto-decrements user flair if post karma is below link/self threshold
* Adds post warning to link posts without descriptions after warning thresold
* Removes link posts without descriptions after removal threshold
* Note: "Help" posts immune to link removal rule based on keywords in post
* Note: Moderators and certain users are immune to link rules and ban requests
