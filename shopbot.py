#!/usr/bin/env python
import re, requests, codecs, os, time, smtplib, sys
from bs4 import BeautifulSoup

def notify(fromname, fromemail, toname, toemail, subject, body, password):
	fromaddr = fromname+" <"+fromemail+">"
	toaddrs = [toname+" <"+toemail+">"]
	msg = "From: "+fromaddr+"\nTo: "+toemail+"\nMIME-Version: 1.0\nContent-type: text/plain\nSubject: "+subject+"\n"+body

	# Credentials (if needed)
	username = fromemail
	password = password

	# The actual mail send
	try:
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.starttls()
		server.login(username,password)
		server.sendmail(fromaddr, toaddrs, msg)
		server.quit()       
		print "Email notification sent"
	except smtplib.SMTPException:
		print "FAIL: Email notificaiton failed to send"       

def checkProduct(m, fromname, fromemail, toname, toemail, password):
	r = requests.get("http://www.shopbot.ca/m/?m=" + m)
	html = r.text.encode('utf-8')
	soup = BeautifulSoup(html)
	imgdata = soup.find("div", "col-img")
	name = re.sub(r'^.*?alt=[\"](.*?)[\"].*?$', r'\1', str(imgdata.img), re.M)
	img = re.sub(r'^.*?src=[\"](.*?)[\"].*?$', r'\1', str(imgdata.img), re.M)
	model = soup.h1(text=True)[0]
	pricedata = soup.find_all("div", "price", text=True)
	#print name
	#print img
	#print model
	prices = []
	for x in pricedata:
		prices.append(re.sub(r'^.*?data-price=[\"\']([\d.]+)[\"\'].*$', r'\1', str(x)))

	lowestprice = min(prices)

	with open("shopbot-"+model+".txt", "a") as f:
		f.write(lowestprice + "\n")

	f.close

	with open("shopbot-"+model+".txt") as f:
		pricehistory = f.readlines()

	f.close

	if len(pricehistory) > 1:
		prevlowestprice = min(pricehistory)

		if float(prevlowestprice) > float(lowestprice):
			print "New lower price found for " + model + ": $" + lowestprice
			if not os.path.exists("shopbot"):
				os.makedirs("shopbot")
			#os.rename("shopbot-"+model+".txt", "shopbot/shopbot-"+model+".txt." + time.strftime("%Y%m%d_%H%M%S"))
			
			subject = "Woo! $" + lowestprice + " for " + name
			body = "\n\n" + model + " -- (" + name + ") dropped in price! It's now $" + lowestprice + ".\n\n" + "Link: http://www.shopbot.ca/m/?m=" + model

			notify(fromname, fromemail, toname, toemail, subject, body, password) 

		else:
			print "No price changes were found for " + model + "."
	else:
		print "(Re)setting price list for " + model + ". This is either the first time checking for the product or a lower price was previously found."

# ----------- DO NOT EDIT ANYTHING ABOVE THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING ------------ #

fromname = "Shopbot Watcher"
fromemail = "yourgmailaccount@gmailorcustomdomain.com" # configure your email address here
toname = "Your Name" # configure the recipient name here
toemail = "recipient@email.com" # configure the recipient email address here - might be the same as fromemail
password = "yourpassword!"

productsToCheck = ["CMSA16GX3M2A1600C11", "MZ-7TE1T0BW"] # configure this array with part number of the items you wish to monitor

# ----------- DO NOT EDIT ANYTHING BELOW THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING ------------ #

for p in productsToCheck:
	checkProduct(p, fromname, fromemail, toname, toemail, password)
