# Meeting timer for Tidbyt

## To make this work

First, follow instructions for creating an app for accessing the
calendar as described in this [Quickstart
overview](https://developers.google.com/calendar/api/quickstart/python).
When done, you should have saved a `credentials.json` file in the same
folder as the script.  On the first run of the script, you'll be
prompted to authenticate.

## How it works

* Look for events in the primary calendar
* Look for ones that have a videoconference link
* If it's happening now, compute the number of minutes left
* Create the right image to send up to the Tidbyt
