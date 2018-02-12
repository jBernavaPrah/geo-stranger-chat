from flask import render_template, url_for

from utilities import mailer


def send_mail_to_admin(template, **params):
	params['EMAIL_TO'] = 'info@geostranger.com'

	data = {
		'Messages': [
			{
				"From": {
					"Email": "info@geostranger.com",
					"Name": "Info GeoStranger.com"
				},
				"To": [
					{
						"Email": "info@geostranger.com",
						"Name": "Info GeoStranger.com"
					}
				],
				"Subject": 'Contact Us',
				"TextPart": "",
				"HTMLPart": render_template('emails/%s.html' % template, **params)
			}
		]
	}
	result = mailer.send.create(data=data)
	return result.json()


def send_mail_to_user(template, user_mail, **params):
	return True
