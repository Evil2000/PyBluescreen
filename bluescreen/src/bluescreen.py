#!/usr/local/bin/python3
# encoding: utf-8
'''
bluescreen -- Locks your screen
bluescreen is a little python script which locks your screen as long as a bluetooth device is disconnected.
It also unlocks the screen when you return.
It uses the DBus to check if the device is connected and it locks the screen through DBus message calls.
The script uses the first BT adapter found in the system, mainly "hci0". This might be incorrect on some systems.
If so, check the source code below and do the necessary changes.
You might also use the tool "d-feet" to explore and debug the DBus.

@author:     dave
@copyright:  2017 dave
@license:    LGPL
@contact:    david.schueler@schueler.homeip.net
@deffield    updated: 08.09.2017
'''

import time
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GObject as gobject
from pprint import pprint

'''
Debug flag should be clear
1 = Verbose
2 = Debug
'''
DEBUG = 1

'''
The BT MAC address of the device to monitor
'''
MAC = "A4:70:D6:71:FC:F6"

''' =================================================================================================================== '''

# Replace : with _ in device MAC address
DEV_ID = MAC.replace(":", "_")
# Access the DBus main loop
dbus_loop = DBusGMainLoop()
# Connect to the system bus
sysbus = dbus.SystemBus(mainloop=dbus_loop)
# Retrieve the device BlueZ object
device = sysbus.get_object('org.bluez', "/org/bluez/hci0/dev_" + DEV_ID)

# Read the property if the device is connected
bt_device = { 'Connected': device.Get("org.bluez.Device1", "Connected", dbus_interface='org.freedesktop.DBus.Properties') }

if DEBUG:
    print("["+time.strftime('%Y-%m-%d %H:%M:%S')+"] BT device is currently connected: "+str(bool(bt_device.get('Connected'))))

# Lock the screen and start the screen saver (i.e. turn off the screen) if it isn't already
def lockScreen():
    # Connect to the session bus
    sesbus = dbus.SessionBus(mainloop=dbus_loop)
    # Get the screen saver object
    sSaver = sesbus.get_object('org.gnome.ScreenSaver', "/org/gnome/ScreenSaver")
    if not sSaver.GetActive(dbus_interface='org.gnome.ScreenSaver'):
        if DEBUG:
            print("["+time.strftime('%Y-%m-%d %H:%M:%S')+"] Locking Screen")
        sSaver.Lock(dbus_interface='org.gnome.ScreenSaver')
    sesbus.close()

def unlockScreen():
    # Connect to the session bus
    sesbus = dbus.SessionBus(mainloop=dbus_loop)
    # Get the screen saver object
    sSaver = sesbus.get_object('org.gnome.ScreenSaver', "/org/gnome/ScreenSaver")
    if sSaver.GetActive(dbus_interface='org.gnome.ScreenSaver'):
        if DEBUG:
            print("["+time.strftime('%Y-%m-%d %H:%M:%S')+"] Unlocking Screen")
        sSaver.SetActive(False, dbus_interface='org.gnome.ScreenSaver')
    sesbus.close()

# Try to connect to the device if it got disconnected. This is called from gobject.timeout_add_seconds() below
def tryConnect():
    try:
        if not bt_device.get('Connected'):
            if DEBUG:
                print("["+time.strftime('%Y-%m-%d %H:%M:%S')+"] Trying device reconnect")
            device.Connect(dbus_interface='org.bluez.Device1')
    except dbus.exceptions.DBusException as e:
        pprint(e)

    return True

# The callback function from connect_to_signal. This handles the events sent by the DBus.
def cb(*args, **kwargs):
    iface = args[0]
    chgprop = args[1]
    #extra = args[2]
    if DEBUG > 1:
        pprint(iface)
        pprint(chgprop)

    # chgprop contains a dictionary with the "Connected" key
    # If it is present and the interface in which the event triggered is Device1, then...
    if iface == "org.bluez.Device1" and "Connected" in chgprop:
        # ... lock screen if device is NOT connected, otherwise disable the screen saver
        if chgprop['Connected'] == True:
            print("["+time.strftime('%Y-%m-%d %H:%M:%S')+"] connected")
            bt_device['Connected'] = True
            unlockScreen()
        else:
            print("["+time.strftime('%Y-%m-%d %H:%M:%S')+"] disconnected")
            bt_device['Connected'] = False
            lockScreen()

# Register a callback function which is triggered if the properties of the bluetooth device changes.
device.connect_to_signal("PropertiesChanged", cb, dbus_interface=None, interface_keyword='iface', member_keyword='member', path_keyword='path', sender_keyword="sender", destination_keyword="dest", message_keyword="message")

# Every 3 seconds, call the tryConnect function
gobject.timeout_add_seconds(3, tryConnect)

# Now, start the main loop.
loop = gobject.MainLoop()
try:
    loop.run()
except KeyboardInterrupt:
    print("Closing program")
finally:
    sysbus.close()
    exit

# EOF
