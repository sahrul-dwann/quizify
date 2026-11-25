from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nama pengguna'
        self.fields['password1'].label = 'Kata sandi'
        self.fields['password2'].label = 'Ulangi kata sandi'
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nama pengguna'
        self.fields['password'].label = 'Kata sandi'
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
