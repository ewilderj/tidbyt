import datetime
import os.path
import json
import yaml

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dateutil import parser

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

CMD = "pixlet render timer.star minutes="
PUSH = "pixlet push "
# Default business hours
DEFAULT_BUSINESS_HOURS = {
    "valid_days": [0, 1, 2, 3, 4],  # Monday to Friday
    "start_hour": 7,
    "end_hour": 17,
}

# general configuration variables
any_event = False # if False, only events with video calls will be monitored
device_id = None # the Tidbyt device ID to push to
calendar_id = "primary" # the calendar ID to fetch events from
business_hours = DEFAULT_BUSINESS_HOURS  # Start with the defaults

def is_within_business_hours(now, business_hours):
    """Checks if the current time is within the configured business hours."""
    day_of_week = now.weekday()
    hour_of_day = now.hour

    if day_of_week not in business_hours["valid_days"]:
        return False

    return (business_hours["start_hour"] <= hour_of_day <= business_hours["end_hour"])

def get_time_left_in_current_meeting(event):
  """Calculate the time left in the current meeting."""
  now = datetime.datetime.now(datetime.timezone.utc)
  end_time_str = event["end"].get("dateTime", event["end"].get("date"))
  end_time = parser.isoparse(end_time_str)
  time_left = end_time - now
  return int((time_left.total_seconds() + 60) / 60)

def send_duration_to_display(duration):
  # set a flag to determine whether we push or not. if we're >= 7
  # minutes out, we only want to send it if we're a multiple of 5
  # minutes if we're < 7 minutes then yes we'll always send it

  send_flag = False
  if duration < 7 or (duration % 5 == 0):
    send_flag = True

  if send_flag:
    print("Sending at", duration)
    cmd = CMD + str(duration)
    os.system(cmd)
    os.system(PUSH)
  else:
    print("Not sending at", duration)

def main():
  # We only want to run this in business hours
  now = datetime.datetime.now()
  if not is_within_business_hours(now, business_hours):
    print("Not in business hours")
    return

  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  # print("Logged in, trying...")

  try:
    # if events.yml exists and is less than 10 minutes old, use it to
    # populate events, otherwise fetch from Google
    events = None
    used_cache = False
    if os.path.exists("events.yml"):
      file_age = os.path.getmtime("events.yml")
      now = datetime.datetime.now().timestamp()
      if now - file_age < 600:
        # print("Using cached events")
        with open("events.yml", "r") as f:
          events = yaml.safe_load(f)
        used_cache = True

    # Get the start and end of the current day in UTC
    now = datetime.datetime.now(datetime.timezone.utc)

    if events is None:
      # print("Starting something")
      service = build("calendar", "v3", credentials=creds)

      start_of_day = datetime.datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=datetime.timezone.utc)
      end_of_day = datetime.datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=datetime.timezone.utc)
      time_min = start_of_day.isoformat()
      time_max = end_of_day.isoformat()

      # print("Getting today's events")
      events_result = (
        service.events()
        .list(
          calendarId=calendar_id,
          timeMin=time_min,
          timeMax=time_max,
          singleEvents=True,
          orderBy="startTime",
        )
        .execute()
      )
      events = events_result.get("items", [])

    if not events:
      print("No events found for today.")
      return

    # serialize events into events.yml
    if not used_cache:
      with open("events.yml", "w") as f:
        yaml.dump(events, f)

    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))

      if "date" in event["start"]:
        # print("Skipping all-day event")
        continue

      print("📅", start, "👀") # , event["summary"])

      video = None
      # Check if the event has a video call attached
      if "conferenceData" in event:
        conference_data = event["conferenceData"]
        if "entryPoints" in conference_data:
          for entry_point in conference_data["entryPoints"]:
            if entry_point["entryPointType"] == "video":
              # print(f"Video call link: {entry_point['uri']}")
              video = entry_point['uri']

      if not any_event and video is None:
        # print("Skipping non-video event")
        continue

      # Check if the event is currently ongoing
      start_time_str = event["start"].get("dateTime", event["start"].get("date"))
      end_time_str = event["end"].get("dateTime", event["end"].get("date"))
      start_time = parser.isoparse(start_time_str)
      end_time = parser.isoparse(end_time_str)
      print(start_time, end_time, now)
      if start_time <= now <= end_time:
        time_left = get_time_left_in_current_meeting(event)
        # print(f"Time left in the current meeting: {time_left}")
        send_duration_to_display(time_left)
        break

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  with open("config.json") as f:
    data = json.load(f)
    calendar_id = data["calendar_id"]
    device_id = data["device_id"]
    PUSH = PUSH + data["device_id"] + " timer.webp"
    if "any_event" in data:
      any_event = data["any_event"] == 1
    if "business_hours" in data:
      business_hours = data["business_hours"]

      # Validate the business hours data (optional but recommended)
      if not isinstance(business_hours.get("valid_days"), list):
        print("Error: 'valid_days' in config.json must be a list of integers (0-6). Using defaults.")
        business_hours = DEFAULT_BUSINESS_HOURS
      else:
        for day in business_hours["valid_days"]:
          if not isinstance(day, int) or not 0 <= day <= 6:
            print("Error: 'valid_days' must contain integers between 0 and 6. Using defaults.")
            business_hours = DEFAULT_BUSINESS_HOURS
            break # exit the loop if there's an invalid day

      if not isinstance(business_hours.get("start_hour"), int) or not 0 <= business_hours["start_hour"] <= 23:
        print("Error: 'start_hour' in config.json must be an integer between 0 and 23. Using defaults.")
        business_hours = DEFAULT_BUSINESS_HOURS

      if not isinstance(business_hours.get("end_hour"), int) or not 0 <= business_hours["end_hour"] <= 23:
        print("Error: 'end_hour' in config.json must be an integer between 0 and 23. Using defaults.")
        business_hours = DEFAULT_BUSINESS_HOURS
  main()
