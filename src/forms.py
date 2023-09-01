from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, DateField, \
    FloatField, FileField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from src.config import ALLOWED_EXTENSIONS
from src.models import User


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    password2 = PasswordField('Powtórz hasło', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Zarejestruj')


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Użyj innego adresu email.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    remember_me = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj')


class MeterForm(FlaskForm):
    radio_number = StringField('Radio Number', validators=[DataRequired()])
    type = SelectField('Type', choices=[('water', 'Wodomierz'), ('heat', 'Ciepłomierz')], validators=[DataRequired()])
    user_id = IntegerField('User ID', validators=[DataRequired()])
    submit = SubmitField('Add Meter')

class MeterReadingForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    reading = FloatField('Reading', validators=[DataRequired()])
    meter_id = IntegerField('Meter ID', validators=[DataRequired()])
    submit = SubmitField('Add Reading')

class UploadForm(FlaskForm):
    device_type = SelectField('Typ pliku', choices=[('water', 'Wodomierz'), ('heat', 'Ciepłomierz'), ('events_water', 'Zdarzenia wodomierze'), ('events_heat', 'Zdarzenia ciepłomierze')], validators=[DataRequired()])
    file = FileField('Plik CSV', validators=[FileRequired(), FileAllowed(ALLOWED_EXTENSIONS), DataRequired()])
    submit = SubmitField('Prześlij')

class UserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    confirm_password = PasswordField('Potwierdź hasło', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Dodaj')

class EditAccountForm(FlaskForm):
    current_password = PasswordField('Obecne hasło', validators=[DataRequired()])
    new_password = PasswordField('Nowe hasło', validators=[DataRequired()])
    confirm_password = PasswordField('Powtórz nowe hasło', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Zmień hasło')

class AddUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    confirm_email = StringField('Confirm Email', validators=[DataRequired(), Email(), EqualTo('email')])
    submit = SubmitField('Add User')

class SetPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Set Password')

class UserNotesForm(FlaskForm):
    notes = TextAreaField('Notatki')

class UserOverviewForm(FlaskForm):
    notes = TextAreaField('Notatki')



class MessageForm(FlaskForm):
    subject = StringField('Temat', validators=[DataRequired()])
    content = TextAreaField('Treść', validators=[DataRequired()])
    recipient = SelectField('Odbiorca', choices=[], validators=[DataRequired()])
    send_to_all = BooleanField('Wyślij do wszystkich')
    submit = SubmitField('Wyślij')

