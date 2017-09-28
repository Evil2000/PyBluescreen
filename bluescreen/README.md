# PyBluescreen
Locks your screen as long as a bluetooth device is disconnected

PyBluescreen is a little python script which locks your screen as long as a bluetooth device is disconnected.
It also unlocks the screen when you return.
It uses the DBus to check if the device is connected and it locks the screen through DBus message calls.
The script uses the first BT adapter found in the system, mainly "hci0". This might be incorrect on some systems.
If so, check the source code and do the necessary changes.
You might also use the tool "d-feet" to explore and debug the DBus.

Since the bluetooth signal strength (RSSI) is only reported for non paired devices it is not used by this script.
Since the link quality is not reported through the DBus system ot is also not used by this script. For this to work the BlueZ sourcecode has to be modified.