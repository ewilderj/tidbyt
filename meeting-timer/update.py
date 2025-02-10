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

def get_time_left_in_current_meeting(event):
  """Calculate the time left in the current meeting."""
  now = datetime.datetime.now(datetime.timezone.utc)
  end_time_str = event["end"].get("dateTime", event["end"].get("date"))
  end_time = parser.isoparse(end_time_str)
  time_left = end_time - now
  return int(time_left.total_seconds() / 60)

CMD = "pixlet render timer.star minutes="
PUSH = "pixlet push "

any_event = False
device_id = None
calendar_id = None

def send_duration_to_display(duration):
  # logic on what we want here let's set a flag to determine whether
  # we push or not if we're > 7 minutes out, we only want to send it
  # if we're a multiple of 5 minutes if we're <= 7 minutes then yes
  # we'll always send it

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
  if now.weekday() > 4 or now.hour < 7 or now.hour > 17:
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
      # print("Found events.json")
      file_age = os.path.getmtime("events.yml")
      now = datetime.datetime.now().timestamp()
      if now - file_age < 600:
        print("Using cached events")
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
          # conferenceDataVersion=1
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
  # print(f"Config:\n\tcalendar {calendar_id}\n\tdevice {device_id}\n\tany_event {any_event}")
  main()
