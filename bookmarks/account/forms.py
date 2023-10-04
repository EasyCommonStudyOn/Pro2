from django import forms
from django.contrib.auth.models import User
from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']

    def clean_password2(self):
        cd = self.cleaned_data

        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd[
            'password2']  # Мы определили метод clean_password2(), чтобы сравнивать второй пароль с первым и выдавать ошибки валидации, если пароли не совпадают.


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo']
"""
UserEditForm позволит пользователям редактировать свое имя, фами-
лию и адрес электронной почты, которые являются атрибутами встро-
енной в Django модели User;
• ProfileEditForm позволит пользователям редактировать данные про-
филя, сохраненные в конкретно-прикладной модели Profile. Пользо-
ватели смогут редактировать дату своего рождения и закачивать изо-
ражение на сайт в качестве фотоснимка профиля."""