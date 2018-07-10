#!/usr/bin/python3

import telebot
from telebot import types
import time
import os

import sys
import Adafruit_DHT
import requests
import httplib, urllib

# Variable that store the bot's token
TOKEN = ""

# Variables that stores the data of the usernames:
userStep = {}
knowUsers = []

# Sensor type and connected GPIO pin:
sensor = 
pin = 

# Instructions of any sensor type:
sensor_args = { '11': Adafruit_DHT.DHT11,
                '22': Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302 }

# Parameter that store if the automatic mode is on:
automat = False     # On the beginning the data is uploaded manualy

# Actualization period:
per = 15 # Second
perTemp = per

# Sensor:
humidity = 0
temperature = 0

# Function to send data to a server:
def sendData():
    # The data is taken from the sensor:
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    

    # The data is sent to user
    bot.send_message('Temp={0:0.1f}  Humidity={1:0.1f}%'.format(temperature, humidity))

    # The parameters are saved in a dictionary (key = thingspeak key)
    params = urllib.urlencode({'field1': temperature, 'field2': humidity, 'key': ''})

    # The text format is selected
    headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
    
    # The connection address is saved (DNS:port)
    conn = httplib.HTTPConnection("api.thingspeak.com:80")
    
    try:
        # Connect to server:
        conn.request("POST", "/update", params, headers)
        # Save response:
        response = conn.getresponse()
        # Show response on terminal
        print (response.status, response.reason)
        data = response.read()
        # Close connection
        conn.close()
        
    except:
        # Error message is shown on the terminal:
        print ("Connection failed")

# Telegrame's bot:

# Bot's basic commands:
commands = {
    'start': 'Activates the bot',
    'help': 'Shows the available commands',
    'show_data': 'Shows the humidity and temperature',
    'up_data': 'Up data to thingspeak server',
    'automatic_mode': 'Activates the automatic mode'}

menu = types.ReplyKeyboardMarkup()
menu.add("Get data", "Automatic mode") # Menu buttons

# Function that check if the incomming user is a new user or old user:
def get_user_step(uid):
    
    if uid in userStep:         # If it is not the first time this user enter returns his/her user ID (uid)
        return userStep[uid]
    
    else:                       # If it's a new user
        knowUsers.append(uid)   # Puts the user in the list
        userStep[uid] = 0       # Assigns 0 value to user ID
        # Prints "New user" in the terminal:
        print (color.RED + "[i] NEW USER!!!" + color.ENDC)

# LISTENER: function that will read when a command enters:
def listener(messages):
    for m in messages:
        if m.content_type == 'text': # Checks if the message is text type
            # Prints message in the terminal:
            print("[" + str(m.chat.id) + "] " + str(m.chat.first_name) + ": " + m.text)

bot = telebot.TeleBot(TOKEN)
bot.set_update_listener(listener)

# START
@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id         # Gets user ID
    userStep[cid] = 0       # Puts user's step in the principal menu (0)
    # The bot sends a message to the user:
    bot.send_message(cid, "Choose:", reply_markup=menu_menu)

# help
@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    # Sends help text:
    help_text = "Available commands: \n"
    for key in commands:
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text) # Sends help message

# Beginning menua
menu_menu = types.ReplyKeyboardMarkup()
menu_menu.add("Get data", "Up data")
menu_menu.add("Change automatic mode", "Activate/deactivate alarm")
menu_menu.add("help")
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 0)
def main_menu(m):    # Principal menu's function
    cid = m.chat.id
    txt = m.text
    global alarm
    if txt == "/show_data" or txt == "Get data": # Button to get data
        bot.send_message(cid, "Reading data...", reply_markup=jaso_menu)
        userStep[cid] = 1 # Changes menu number
    elif txt == "/up_data" or txt == "Up data": # Button to up data
        bot.send_message(cid, "Uploading data...")
        userStep[cid] = 2 # Changes menu number
    elif txt == "/automatic_mode" or txt == "Change automatic mode": # Automatic mode button
        if automat == False:
            bot.send_message(cid, "Turn the automatic mode from off to on\n\n(Automatic mode: off)", reply_markup=autom_menu)
        elif automat == True:
            bot.send_message(cid, "Turn the automatic mode from on to off\n\n(Automatic mode: on)", reply_markup=autom_menu)
        userStep[cid] = 3 # Changes menu number
    elif txt == "Activate/deactivate alarm":
        bot.send_message(cid, "Choose the temperature to activate alarm")
        bot.send_message(cid, "Give it the temperature where the risk begins", reply_markup=alarmT_menu)
        alarm = 1
        userStep[cid] = 5 # Changes menu number
    elif txt == "help":   # Opens help menu
        command_help(m)
    else:
        command_start(m)

jaso_menu = types.ReplyKeyboardMarkup()
jaso_menu.add("Temperature", "Humidity", "Both")
jaso_menu.add("Return to beginning")
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 1)
def jaso_opt(m):
    cid = m.chat.id     # User ID
    txt = m.text        # Receibed message
    if txt == "Temperature":
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        #show_data()
        bot.send_message(cid, "Room temperature: %s" % temperature )
    elif txt == "Humidity":
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        #show_data()
        bot.send_message(cid, "Relative humidity: %s" % humidity )
    elif txt == "Both":
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        #show_data()
        bot.send_message(cid, "Room temperature: %s" % temperature )
        bot.send_message(cid, "Relative humidity: %s" % humidity )
    else:
        command_start(m)

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 2)
def up_opt(m):
    cid = m.chat.id     # User ID
    bot.send_message(cid, "Sending..." )
    # Get data from sensor:
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

    # Show data to user:
    bot.send_message(cid, 'Temp={0:0.1f}  Humidity={1:0.1f}%'.format(temperature, humidity))

    # Show data on terminal:
    print ('Temp={0:0.1f}  Humidity={1:0.1f}%'.format(temperature, humidity))

    # The parameters are saved in a dictionary (key = thingspeak key)
    params = urllib.urlencode({'field1': temperature, 'field2': humidity, 'key': ''})

    # The text format is selected
    headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
    
    # The connection address is saved (DNS:port)
    conn = httplib.HTTPConnection("api.thingspeak.com:80")

    try:
        # Connect to server:
        conn.request("POST", "/update", params, headers)
        # Save response:
        response = conn.getresponse()
        # Show response on terminal
        print (response.status, response.reason)
        data = response.read()
        # Close connection
        conn.close()
        
    except:
        # Error message is shown on the terminal:
        print ("Connection failed")
        # Error message is sent to user:
        bot.send_message(cid, "Connection error!")
        
    command_start(m)

autom_menu = types.ReplyKeyboardMarkup()
autom_menu.add("Activate", "Deactivate")
autom_menu.add("Choose period", "Return to beginning")

aldatu_menu = types.ReplyKeyboardMarkup()
aldatu_menu.add("Yes", "No")

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 3)
def autom_opt(m):
    global automat
    global per
    cid = m.chat.id     # User ID
    txt = m.text        # Receibed message
    if txt == "Activate":
        if automat == False:
            automat = True
            bot.send_message(cid, "Automatic mode has been activated with a period of %s seconds " % per)
            sendInCycle()
        elif automat == True:
            bot.send_message(cid, "Automatic mode is activated already! (Period: %s seconds)" % per)
    elif txt == "Deactivate":
        if automat == True:
            automat = False
            bot.send_message(cid, "Automatic mode has been deactivated")
            command_start(m)
        elif automat == False:
            bot.send_message(cid, "Automatic mode is deactivated already!")
            command_start(m)
    elif txt == "Choose period":
        bot.send_message(cid, "Choose period (actual period: %s second)" % per, reply_markup=period_menu)
        userStep[cid] = 4
    elif txt == "Return to beginning":
        command_start(m)

period_menu = types.ReplyKeyboardMarkup()
period_menu.add("+1s", "+15s", "+30s", "+1min")
period_menu.add("+5min", "+15min", "+30min", "+1h")
period_menu.add("-1s", "-15s", "-30s", "-1min")
period_menu.add("-5min", "-15min", "-30min", "-1h")
period_menu.add("Ok", "Leave as was")
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 4)
def denbora_opt(m):
    cid = m.chat.id
    txt = m.text
    global per
    global perTemp
    if txt == ("%s", per):
        per = perTemp
        bot.send_message(cid, "Choose period: %s second" % per)
        command_start(m)
    elif txt == "+1s":
        perTemp = perTemp + 1
        if perTemp > 432100:
            perTemp = 432100
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "+5s":
        perTemp = perTemp + 5
        if perTemp > 432100:
            perTemp = 432100
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "+15s":
        perTemp = perTemp + 15
        if perTemp > 432100:
            perTemp = 432100
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "+30s":
        perTemp = perTemp + 30
        if perTemp > 432100:
            perTemp = 432100
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "+1min":
        perTemp = perTemp + 60
        if perTemp > 432100:
            perTemp = 432100
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "+5min":
        perTemp = perTemp + 3000
        if perTemp > 432100:
            perTemp = 432100
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "+15min":
        perTemp = perTemp + 15000
        if perTemp > 432100:
            perTemp = 432100
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "+30min":
        perTemp = perTemp + 30000
        if perTemp > 432100:
            perTemp = 432100
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "+1h":
        perTemp = perTemp + 60000
        if perTemp > 432100:
            perTemp = 432100
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "-1s":
        perTemp = perTemp - 1
        if perTemp < 1:
            perTemp = 1
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "-5s":
        perTemp = perTemp - 5
        if perTemp < 1:
            perTemp = 1
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "-15s":
        perTemp = perTemp - 15
        if perTemp < 1:
            perTemp = 1
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "-30s":
        perTemp = perTemp - 30
        if perTemp < 1:
            perTemp = 1
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "-1min":
        perTemp = perTemp - 60
        if perTemp < 1:
            perTemp = 1
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "-5min":
        perTemp = perTemp - 3000
        if perTemp < 1:
            perTemp = 1
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "-15min":
        perTemp = perTemp - 15000
        if perTemp < 1:
            perTemp = 1
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "-30min":
        perTemp = perTemp - 30000
        if perTemp < 1:
            perTemp = 1
        bot.send_message(cid, "Period: %s second" % perTemp)
    elif txt == "-1h":
        perTemp = perTemp - 60000
        if perTemp < 1:
            perTemp = 1
        bot.send_message(cid, reply_markup=period_menu)
    elif txt == "Ok":
        per = perTemp
        bot.send_message(cid, "Period %s second dira orain" % per)
        command_start(m)
    elif txt == "Leave as was":
        bot.send_message(cid, "Period %s secondtan utzi da" % per)
        command_start(m)

# Function that, if automatic mode is allowed, upload data to the server:
def sendInCycle():
    global automat
    global warning
    while True:
        if automat == True:
            # Show data in terminal
            print ('Temp={0:0.1f}  Humidity={1:0.1f}%'.format(temperature, humidity))
            
            # The parameters are saved in a dictionary (key = thingspeak key)
            params = urllib.urlencode({'field1': temperature, 'field2': humidity, 'key': ''})

            # The text format is selected
            headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
            
            # The connection address is saved (DNS:port)
            conn = httplib.HTTPConnection("api.thingspeak.com:80")
            
            try:
                # Connect to server:
                conn.request("POST", "/update", params, headers)
                # Save response:
                response = conn.getresponse()
                # Show response on terminal
                print (response.status, response.reason)
                data = response.read()
                # Close connection
                conn.close()
                
            except:
                # Error message is shown on the terminal:
                print ("Connection failed")
            
            # Wait the period:
            time.sleep(per)

alarm = 0
warning = False
alarmL = 28
alarmH = 30
alarmActivated = False

alarmT_menu = types.ReplyKeyboardMarkup()
alarmT_menu.add("Temperature to turn on the alarm", "Temperature to turn off the alarm")
alarmT_menu.add("TH + 1", "TL + 1")
alarmT_menu.add("TH + 10", "TL + 10")
alarmT_menu.add("TH - 1", "TL - 1")
alarmT_menu.add("TH - 10", "TL - 10")
alarmT_menu.add("Ok", "Return")
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 5)
def warningCheck(m):
    global alarmL
    global alarmH
    global alarm
    global alarmActivated
    cid = m.chat.id
    txt = m.text
    if txt == "Temperature to turn on the alarm":
            bot.send_message(cid, "% s" % alarmH)
    elif txt == "Temperature to turn off the alarm":
            bot.send_message(cid, "% s" % alarmL)
    #TH
    elif txt == "TH + 1":
        alarmH = alarmH +1
        if alarmH > 100:
            alarmH = 100
        bot.send_message(cid, "Temperature to turn on the alarm: %s C" % alarmH)
    elif txt == "TH + 10":
        alarmH = alarmH +10
        if alarmH > 100:
            alarmH = 100
        bot.send_message(cid, "Temperature to turn on the alarm: %s C" % alarmH)
    elif txt == "TH - 1":
        alarmH = alarmH - 1
        if alarmH <= -14:
            alarmH = -14
        if alarmH <= alarmL:
            alarmH = alarmL + 1
        bot.send_message(cid, "Temperature to turn on the alarm: %s C" % alarmH)
    elif txt == "TH - 10":
        alarmH = alarmH - 10
        if alarmH <= -14:
            alarmH = -14
        if alarmH <= alarmL:
            alarmH = alarmL + 1
        bot.send_message(cid, "Temperature to turn on the alarm: %s C" % alarmH)
    # TL
    elif txt == "TL + 1":
        alarmL = alarmL +1
        if alarmL > 99:
            alarmL = 99
        if alarmL >= alarmH:
            alarmL = alarmH - 1
        bot.send_message(cid, "Temperature to turn off the alarm: %s C" % alarmL)
    elif txt == "TL + 10":
        alarmL = alarmL +10
        if alarmL > 99:
            alarmL = 99
        if alarmL >= alarmH:
            alarmL = alarmH - 1
        bot.send_message(cid, "Temperature to turn off the alarm: %s C" % alarmL)
    elif txt == "TL - 1":
        alarmL = alarmL - 1
        if alarmL <= -15:
            alarmL = -15
        bot.send_message(cid, "Temperature to turn off the alarm: %s C" % alarmL)
    elif txt == "TL - 10":
        alarmL = alarmL - 10
        if alarmL <= -15:
            alarmL = -15
        bot.send_message(cid, "Temperature to turn off the alarm: %s C" % alarmL)
    elif txt == "Ok":
        alarmActivated = True
        bot.send_message(cid, "Alarm activated (press 'Start' button to begin)")
        bot.send_message(cid, "Temperature to turn on the alarm: %s C" % alarmH)
        bot.send_message(cid, "Temperature to turn off the alarm: %s C" % alarmL)
        bot.send_message(cid, "Hysteresis = %s" % (alarmH - alarmL), reply_markup=alarm_menu)
        userStep[cid] = 6
    elif txt == "Return":
        command_start(m)
    
        
alarm_menu = types.ReplyKeyboardMarkup()
alarm_menu.add("Start", "Turn off alarm")
alarm_menu.add("Change alarm", "Show temperature")
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 6)
def warningNotify(m):
    global alarmL
    global alarmH
    global warning
    global alarmActivated
    cid = m.chat.id
    txt = m.text
    while alarmActivated == True:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        if temperature >= alarmH and warning == False:
            bot.send_message(cid, "WARNING: TEMPERATURE HAS OVERCOME %s C!" %alarmH)
            warning = True
        if temperature <= alarmL and warning == True:
            bot.send_message(cid, "The danger has passed (temperature: %s C)" % temperature)
            warning = False
        if txt == "Start":
            alarmActivated = True
        elif txt == "Turn off alarm":
            alarmActivated = False
            bot.send_message(cid, "The alarm has been turned off")
            command_start(m)
        elif txt == "Show temperature":
            bot.send_message(cid, "%s C" % temperature)
        elif txt == "Change alarm":
            alarmActivated = False
            warning = False
            bot.send_message(cid, "Choose temperature to activate/deactivate alarm")
            bot.send_message(cid, "Choose temperature to turn off the alarm", reply_markup=alarmT_menu)
            userStep[cid] = 5
    
bot.polling(none_stop=True)
