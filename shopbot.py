#!/usr/bin/env python

import re, requests, codecs, os, time, smtplib, sys, locale
from bs4 import BeautifulSoup
locale.setlocale(locale.LC_ALL, 'en_CA.UTF-8')

# ---------------------- BEGIN CONFIGURATION - YOU CAN EDIT THESE PARTS! ------------------------- #

fromname = "Shopbot Watcher" # This will be the display name for notification emails
fromemail = "youremail@gmail.com" # The email address you're sending from. If using gmail, this must be your login email
toname = "Your Name" # Display name for the recipient (usually you)
toemail = "youremail@gmail.com" # The recipient's email address (usually your email)
password = "yourP@ssw0rd" # Your gmail password

modelNumbersToCheck = ["CMSA16GX3M2A1600C11", "MZ-7TE250BW", "9000186", "RT-AC68U", "CT2K8G3S160BM 16GB", "ST4000VN000", "CT240M500SSD1", "WD40EFRX", "MZ-7TE1T0BW"]
priceDropThreshold = 1 # Minimum number, in dollars, for price to have dropped before sending notification email

# ----------- DO NOT EDIT ANYTHING BELOW THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING ------------ #

class Product(object):
	def __init__(self, model, name, img, price):
		self.model = model
		self.name = name
		self.img = img
		self.prices = []

	def addPrice(self, price):
		self.prices.append(float(price))

	def addPrices(self, prices):
		self.prices.extend(map(float, prices))

def moneyFromFloat(price):
	return locale.currency(price)

def floatFromMoney(string):
	return '%.2f' % float(re.sub(r'[\$,a-z\s]', r'', str(string), re.I))

def sanitizeName(name):
	return re.sub(r'( - \[.*?\])', r'', str(name), re.I)

def notify(subject, body):
	fromaddr = fromname+" <"+fromemail+">"
	toaddrs = [toname+" <"+toemail+">"]
	msg = "From: "+fromaddr+"\nTo: "+toemail+"\nMIME-Version: 1.0\nContent-type: text/plain\nSubject: "+subject+"\n"+body

	# Credentials (if needed)
	username = fromemail

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

def checkProduct(model):

	#setup
	currentFolder = os.path.dirname(os.path.realpath(__file__)) + "/shopbot_history/"
	if not os.path.exists("shopbot_history"):
		os.makedirs(currentFolder)
	priceHistoryFile = currentFolder + "shopbot-"+model+".txt"

	#url to call
	r = requests.get("http://www.shopbot.ca/m/?m=" + model)
	html = r.text.encode('utf-8')
	soup = BeautifulSoup(html)

	#begin scrape
	product = Product(soup.h1(text=True)[0], sanitizeName(soup.findAll("li", { "class" : "image" })[0].img["alt"]), soup.findAll("li", { "class" : "image" })[0].img["src"], [])
	for x in soup.findAll("div", { "class" : "price" }, text=True):
		product.addPrice(floatFromMoney(x.span.text))

	print product.name + ":"

	if os.path.exists(priceHistoryFile):
		with open(priceHistoryFile, "r") as f:
			lines = f.readlines()
			previousPrice = float(lines[-1])
			f.close()
		
		if (previousPrice == min(product.prices)):
			print "\tNo price changes detected. Currently: " + moneyFromFloat(min(product.prices)) + "\n"

		elif (previousPrice > min(product.prices)):
			print "\tNew lower price detected! Currently: " + moneyFromFloat(min(product.prices)) + "\n"
			if (previousPrice - priceDropThreshold > min(product.prices)):
				subject = "Woo! " + moneyFromFloat(min(product.prices)) + " for " + product.model
				body = "\n\n" + product.name + " has dropped in price! It's now: \n\n" + moneyFromFloat(min(product.prices)) + ".\n\nLink: http://www.shopbot.ca/m/?m=" + model + "\n"
				notify(subject, body)

		elif (previousPrice < min(product.prices)):
			print "\tPrice increase. Currently: " + moneyFromFloat(min(product.prices)) + "\n"
		
		with open(priceHistoryFile, "a") as f:
			f.write(str(min(product.prices)) + "\n")
			f.close()
	else:
		with open(priceHistoryFile, "a") as f:
			f.write(str(min(product.prices)) + "\n")
			f.close()
		print "\tCreated history file. Run this script again to check for price changes.\n"

for model in modelNumbersToCheck:
	checkProduct(model)
