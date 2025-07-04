import json
import datetime
from garminconnect import Garmin
import os

client = Garmin(os.environ["GARMIN_USER"], os.environ["GARMIN_PASS"])
client.login()
today = datetime.date.today()
stats = client.get_stats(today.isoformat())
print(json.dumps(stats, indent=2))
