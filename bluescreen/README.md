# PyBluescreen
Locks your screen as long as a bluetooth device is disconnected

PyBluescreen is a little python script which locks your screen as long as a bluetooth device is disconnected.
It also unlocks the screen when you return.
It uses the DBus to check if the device is connected and it locks the screen through DBus message calls.
The script uses the first BT adapter found in the system, mainly "hci0". This might be incorrect on some systems.
If so, check the source code below and do the necessary changes.
You might also use the tool "d-feet" to explore and debug the DBus.