import calendar

from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, DateField, \
    FloatField, FileField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from src.config import ALLOWED_EXTENSIONS
from src.models import User, Meter

'''
Description: Formularz logowania

'''
class LoginForm(FlaskForm):
    email = StringField('Użytkownik', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    remember_me = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj')


class MeterForm(FlaskForm):
    radio_number = StringField('Radio Number', validators=[DataRequired()])
    type = SelectField('Type', choices=[('water', 'Wodomierz'), ('heat', 'Ciepłomierz')], validators=[DataRequired()])
    user_id = IntegerField('User ID', validators=[DataRequired()])
    submit = SubmitField('Add Meter')


class UploadForm(FlaskForm):
    device_type = SelectField('Typ pliku', choices=[('water', 'Wodomierz'), ('heat', 'Ciepłomierz'),
                                                    ('events_water', 'Zdarzenia wodomierze'),
                                                    ('events_heat', 'Zdarzenia ciepłomierze')],
                              validators=[DataRequired()])
    file = FileField('Plik CSV', validators=[FileRequired(), FileAllowed(ALLOWED_EXTENSIONS), DataRequired()])
    submit = SubmitField('Prześlij')


class UserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    confirm_password = PasswordField('Potwierdź hasło', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Administrator')
    is_superuser = BooleanField('Superuser')
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
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password',
                                                                                                 message='Passwords must match')])
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


class AssignMeterToSuperuserForm(FlaskForm):
    superuser_id = SelectField('Superużytkownik', coerce=int, validators=[DataRequired()])
    meter_id = SelectField('Licznik', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Przypisz Licznik')

    def __init__(self, *args, **kwargs):
        super(AssignMeterToSuperuserForm, self).__init__(*args, **kwargs)
        self.superuser_id.choices = [(u.id, u.email) for u in User.query.filter_by(is_superuser=True).all()]
        self.meter_id.choices = [(m.id, m.radio_number) for m in Meter.query.all()]


class AssignMeterToUserForm(FlaskForm):
    user_id = SelectField('Użytkownik', coerce=int, validators=[DataRequired()])
    meter_id = SelectField('Licznik', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Przypisz Licznik')

    def __init__(self, superuser_id, *args, **kwargs):
        super(AssignMeterToUserForm, self).__init__(*args, **kwargs)
        self.user_id.choices = [(u.id, u.email) for u in User.query.filter_by(superuser_id=superuser_id).all()]
        self.meter_id.choices = [(m.id, m.radio_number) for m in
                                 Meter.query.filter_by(owned_by_superuser=superuser_id).all()]


MONTHS_PL = {
    1: 'Styczeń', 2: 'Luty', 3: 'Marzec',
    4: 'Kwiecień', 5: 'Maj', 6: 'Czerwiec',
    7: 'Lipiec', 8: 'Sierpień', 9: 'Wrzesień',
    10: 'Październik', 11: 'Listopad', 12: 'Grudzień'
}
class EditUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Nowe hasło')  # Usunięto DataRequired
    confirm_password = PasswordField('Potwierdź hasło', validators=[EqualTo('password')])  # Usunięto DataRequired
    report_months = SelectMultipleField('Miesiące raportowania', choices=[(str(i), MONTHS_PL[i]) for i in range(1, 13)],
                                        coerce=int)
    submit = SubmitField('Zaktualizuj')
