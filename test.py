from datetime import datetime, timedelta
import pytz
test = datetime.now(pytz.utc) + timedelta(minutes=2)

print(datetime.now(pytz.utc) - test.minute)
