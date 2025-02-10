# Meeting timer for Tidbyt

## To make this work

First, follow instructions for creating an app for accessing the
calendar as described in this [Quickstart
overview](https://developers.google.com/calendar/api/quickstart/python).
When done, you should have saved a `credentials.json` file in the same
folder as the script.  On the first run of the script, you'll be
prompted to authenticate.

Second, have a Tidbyt dev environment set up [as described
here](https://tidbyt.dev/docs/build/build-for-tidbyt). Configure the
name of the device you're targeting in `device.json`, e.g.

``` json
{"device_id": "my-wonderful-device-id-30c"}
```

## How it works

* Look for events in the primary calendar
* Look for ones that have a videoconference link
* If it's happening now, compute the number of minutes left
* Create the right image to send up to the Tidbyt
