from bottle import Bottle, run, static_file, request
from jinja2 import Environment, FileSystemLoader
from handlers import *
from report_templates import *
import os

app = Bottle()

# GLOBALS
j2_env = Environment(loader=FileSystemLoader(temp_path))


def render(tpl, context):
	return j2_env.get_template(tpl).render(context)


@app.route('/report')
def report():
	dates = get_dates()
	context = {'hours': get_hours(), 'mins': get_minutes(),
	           'since_date': dates[0], 'till_date': dates[1]}
	return render('report.tpl', context)


@app.route('/report', method='POST')
def make_report():
	since = {
		'hour': request.forms.get('since_hour'),
		'minute': request.forms.get('since_min'),
		'date': request.forms.get('since_date')
	}
	till = {
		'hour': request.forms.get('till_hour'),
		'minute': request.forms.get('till_min'),
		'date': request.forms.get('till_date')
	}
	time_period = time_handler(since, till)

	report_type = request.forms.get('type')

	report_format = request.forms.get('format')

	report_class = request.forms.get('report_class')

	if report_class == 'project':
		project = request.forms.get('project')
		reporter = ProjectPeriodReport(
			time_period[0], time_period[1], project,
			report_format=report_format, report_type=report_type
		)
		reporter.generate_report()
	elif report_class == 'item':
		item = request.forms.get('item')
		reporter = ItemPeriodReport(
			time_period[0], time_period[1], item,
			report_format=report_format, report_type=report_type)
		reporter.generate_report()
	else:
		reporter = PeriodReport(
			time_period[0], time_period[1], report_format=report_format,
			report_type=report_type)
		reporter.generate_report()

	return render('status.tpl', {'text': report_ok})


@app.route('/login')
def login():
	try:
		data = p_load()
		if len(data) > 1:
			context = {'host': data['host'], 'user': data['user']}
		else:
			context = {'host': '', 'user': ''}
	except EOFError:
		context = {'host': '', 'user': ''}
	return render('login.tpl', context)


@app.route('/login', method='POST')
def do_login():
	dct = {'host': request.forms.get('host'),
		   'user': request.forms.get('username')}
	password = request.forms.get('password')
	if login_check(dct, password) is True:
		p_handler(dct)
		os.environ['pass'] = password
		return render('status.tpl', {'text': login_ok.format(dct['user'])})
	else:
		return render('status.tpl', {'text': login_fail})


@app.route('/about')
def about():
	context = {'name': 1}
	return render('about.tpl', context)


@app.get('/static/<filename:path>')
def send_static(filename):
	return static_file(filename, root=static_path)


def error404(error):
	return render('status.tpl', {'text': e404})


def error500(error):
	return render('status.tpl', {'text': e500})


handler = {
    500: error500,
	404: error404
}

app.error_handler = handler

# run(app, host='localhost', port=8060, debug=True)

if __name__ == '__main__':
	port = 8060
	from threading import Thread
	app_thread = Thread(target=run, kwargs=dict(app=app, host='localhost', port=port))
	app_thread.start()
	# Open the web browser
	webbrowser.open('http://localhost:{0}/login'.format(port))

