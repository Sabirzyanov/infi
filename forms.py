from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=16)])
    submit = SubmitField('Зарегистрироваться')


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(min=3, max=25)])
    description = StringField('Краткое описание', validators=[DataRequired(), Length(min=3, max=75)])
    content = TextAreaField("Содержание", validators=[Length(min=3, max=10000)])
    tags = StringField('Теги', validators=[DataRequired(), Length(max=50)])
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')


class EditProfileForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=16)])
    status = StringField('Статус', validators=[DataRequired(), Length(max=60)])
    about_me = StringField('Обо мне', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Сохранить')
