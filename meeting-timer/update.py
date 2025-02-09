import datetime
import os.path

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

def send_duration_to_display(duration):
  print(duration)

def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
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
    # print("Starting something")
    service = build("calendar", "v3", credentials=creds)

    # Get the start and end of the current day in UTC
    now = datetime.datetime.now(datetime.timezone.utc)
    start_of_day = datetime.datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=datetime.timezone.utc)
    end_of_day = datetime.datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=datetime.timezone.utc)
    time_min = start_of_day.isoformat()
    time_max = end_of_day.isoformat()

    # print("Getting today's events")
    events_result = (
      service.events()
      .list(
        calendarId="primary",
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


    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))

      if "date" in event["start"]:
        # print("Skipping all-day event")
        continue

      print("📅", start, "👀", event["summary"])

      video = None
      # Check if the event has a video call attached
      if "conferenceData" in event:
        conference_data = event["conferenceData"]
        if "entryPoints" in conference_data:
          for entry_point in conference_data["entryPoints"]:
            if entry_point["entryPointType"] == "video":
              # print(f"Video call link: {entry_point['uri']}")
              video = entry_point['uri']

      if video is None:
        # print("Skipping non-video event")
        continue

      # Check if the event is currently ongoing
      start_time_str = event["start"].get("dateTime", event["start"].get("date"))
      end_time_str = event["end"].get("dateTime", event["end"].get("date"))
      start_time = parser.isoparse(start_time_str)
      end_time = parser.isoparse(end_time_str)
      # print(start_time, end_time, now)
      if start_time <= now <= end_time:
        time_left = get_time_left_in_current_meeting(event)
        # print(f"Time left in the current meeting: {time_left}")
        send_duration_to_display(time_left)
        break

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
