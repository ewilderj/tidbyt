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
name of the device you're targeting, along with the calendar ID and
whether to check if it's a video call or not in `config.json`, e.g.

``` json
{"device_id": "my-wonderful-device-id-30c", "any_event": 0, "calendar_id": "fred@foo.com"}
```

By default, the script only updates the display in business hours
(Mon-Fri, 0900-1700h). You can control this by adding the
`business_hours` key to the `config.json` file, e.g. this makes the
update run from 7am to 6pm on every day of the week.

``` json
    "business_hours": {
        "valid_days": [0, 1, 2, 3, 4, 5, 6],
        "start_hour": 7,
        "end_hour": 18
    }
```


## How it works

* Look for events in the primary calendar
* Look for ones that have a videoconference link, if `any_event` is `0`
  * if `any_event` is `1`, will respect any event
* If it's happening now, compute the number of minutes left
* Create the right image to send up to the Tidbyt

It tries not to be too annoying, so will only send a notification
every 5 minutes, until we get to 6 minutes or less, where the
notification will always send.
