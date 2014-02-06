shopbot-watcher
===============

This simple script scrapes [shopbot.ca](http://shopbot.ca) and tracks price drops. Set it up in a cron job to have it notify you by email.

Dependencies
---
This project requires [BeautifulSoup 4](http://www.crummy.com/software/BeautifulSoup/#Download)

Installation/Configuration
---
Clone the repo and open the shopbot.py file. Change lines 73 - 79 to configure your email account, email recipient, and products you want to monitor.

```python
# you probably don't need to change this, but you can if you want
fromname = "Shopbot Watcher"

# configure your email address here
fromemail = "yourgmailaccount@gmailorcustomdomain.com" 

# configure the recipient name here
toname = "Your Name" 
    
# configure the recipient email address here - might be the same as fromemail
toemail = "recipient@email.com" 
password = "yourpassword!"

# configure this array with part number of the items you wish to monitor
productsToCheck = ["CMSA16GX3M2A1600C11", "MZ-7TE1T0BW"]
```

Cron/Scheduling
---

A simple twice-a-day cron schedule might look something like this:

    * 0,12 * * * "python ~/Downloads/shopbot-watcher/shopbot.py"
    
Working on OSX? Use a tool like [LaunchControl](http://www.soma-zone.com/download/) to schedule scripts.

Constraints
---

 - Out-of-the-box support for parsing shopbot.ca only.
 - Other email providers are untested; change the smtp gateway address to use an alternate provider.
