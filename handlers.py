import pickle
import os
import sys
import subprocess
from pyzabbix import ZabbixAPI
from datetime import datetime
from pathlib import PurePath

# Root app folder path
root_path = os.getcwd()
pure_path_templates = PurePath(root_path).joinpath('templates')
# Path to templates folder
temp_path = str(pure_path_templates)
# Path to log info
log_info_path = str(pure_path_templates.joinpath('log_info.pk'))
# Path to folder with static files
static_path = str(pure_path_templates.joinpath('static'))
# Path to reports folder
report_folder_path = str(PurePath(root_path).joinpath('reports'))


# To open folder with reports on local system
def open_reports_folder():
	# Checking OS, choose the required explorer and open a window
	if sys.platform == 'darwin':
		subprocess.Popen(['open', report_folder_path])
	elif sys.platform == 'linux2':
		subprocess.Popen(['xdg-open', report_folder_path])
	elif sys.platform == 'win32':
		subprocess.Popen(['explorer', report_folder_path])


# Pass time values to the report template
def get_datetime():
	# Current date&time
	today = datetime.now()
	today_str = today.date().strftime("%Y-%m-%d")
	# Till date&time always current time
	till_hour = str(today.hour)
	till_minute = str(today.minute)
	# Check if hour or minute len = 1
	if len(till_hour) == 1:
		till_hour = '0' + till_hour
	if len(till_minute) == 1:
		till_minute = '0' + till_minute
	till_time = till_hour + ':' + till_minute
	till_date = today_str
	# If it's day shift
	if 9 < today.hour <= 21:
		since_date = today_str
		since_time = '09:00'
	# If it's night shift	
	elif today.hour < 9:
		since_date = today.replace(day=today.day - 1).strftime("%Y-%m-%d")
		since_time = '21:00'
		
	else:
		since_time = '21:00'
		since_date = today_str
	
	result = {'since': (since_time, since_date), 'till': (till_time, till_date)}
	return result


# Write data to pk-file
def p_handler(arg):
	with open(log_info_path, 'wb') as f:
		pickle.dump(arg, f)


# Extract data from pk-file
def p_load():
	with open(log_info_path, 'rb') as fl:
		data = pickle.load(fl)
	return data


# Check access to a host and try to get it's version
def login_check(cred, password):
	try:
		z = ZabbixAPI(cred['host'], user=cred['user'], password=password)
		result = True
		# return api version
		api = z.api_version()
	except:
		result = False
		api = None
	return result, api


# Converts incoming reports timestamps
def time_handler(since, till):
	since_date = since['date'].split('-')
	since_time = since['time'].split(':')
	start_time = datetime(
		int(since_date[0]), int(since_date[1]), int(since_date[2]),
		hour=int(since_time[0]), minute=int(since_time[1])
	)
	till_date = till['date'].split('-')
	till_time = till['time'].split(':')
	end_time = datetime(
		int(till_date[0]), int(till_date[1]), int(till_date[2]),
		hour=int(till_time[0]), minute=int(till_time[1])
	)
	return start_time, end_time
	
	
# Status texts

login_ok = '''Hi {0}! You are logged in your Zabbix account.\n'''

login_fail = '''
	Something went wrong. Please check your credentials and operability of a chosen
	Zabbix host and your credentials. \n
	Then try to login again in the Settings section.
'''

e404 = '''
	The page was not found.\n
	Please check the URL or try to reboot this app. \n
'''

report_ok = '''
	The report has been generated.
'''

e500 = '''
	<h3>500 error.</h3> \n
	\n
	<p>Something happened.</p>\n
	<p>Get back and check if you've done your previous actions right. \n
	Otherwise reboot the app and try again. \n</p>
'''
