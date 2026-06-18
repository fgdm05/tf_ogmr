from crontab import CronTab
from datetime import datetime	
cron = CronTab(user=True)
path = f"./cron.py {2} {gateway}"
job = cron.new(command = path)
job.month.on()
job.day.on()
job.hour.on()
job.minute.on()
cron.write()