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

    def clean_email(self):
        data = self.cleaned_data.get('email')

        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already in use.')

        return data

    """
    Мы добавили валидацию поля электронной почты, которая не позволяет
пользователям регистрироваться с уже существующим адресом электронной
почты. Мы формируем набор запросов QuerySet, чтобы свериться, нет ли
существующих пользователей с одинаковым адресом электронной почты.
Мы проверяем наличие результатов посредством метода exists(). Метод exists()
возвращает True, если набор запросов QuerySet содержит какие-либо
результаты, и False в противном случае."""


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        data = self.cleaned_data['email']
        qs = User.objects.exclude(id=self.instance.id).filter(email=data)

        if qs.exists():
            raise forms.ValidationError('Email already in use.')
        return data


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
