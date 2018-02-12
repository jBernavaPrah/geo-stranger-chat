
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, Length, InputRequired

from utilities.mailer import send_mail_to_admin


class BaseForm(FlaskForm):
	pass


# recaptcha = RecaptchaField('Recaptcha Field')


class ContactForm(BaseForm):
	def execute(self):
		send_mail_to_admin(template='contact_us', EMAIL=self.email.data,
																 SUBJECT=self.subject.data,
																 MESSAGE=self.message.data
						   )

	# mail.send_mail(to='info@upvisits.com', reply_to=self.email.data, template=mail.CONTACT, fill={'EMAIL': self.email.data, 'SUBJECT': self.subject.data, 'MESSAGE': self.message.data})

	name = StringField('Your name', validators=[InputRequired(), Length(max=100), DataRequired(), ])
	email = EmailField('Your email', validators=[InputRequired(), Length(max=100), DataRequired(), Email()])
	subject = StringField('Subject', validators=[InputRequired(), Length(max=100), DataRequired()])
	message = TextAreaField('How can we help?', validators=[InputRequired(), Length(max=5000), DataRequired()], )
