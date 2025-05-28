from django import forms


def bootstrap_class(cls):
    def init_(self, *args, **kwargs):
        super(cls, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    cls.__init__ = init_
    cls.template_name = 'vote/form_snippet.html'
    return cls


@bootstrap_class
class LoginForm(forms.Form):
    id = forms.CharField(
        label='ID',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Nhập ID của bạn'})
    )
    password = forms.CharField(
        label='Mật khẩu',
        widget=forms.PasswordInput(attrs={'placeholder': 'Nhập mật khẩu của bạn'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
            field.error_messages = {'required': ''}


@bootstrap_class
class RegisterForm(forms.Form):
    id = forms.CharField(label='ID', max_length=100)
    name = forms.CharField(label='Name', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    email = forms.EmailField(label='Email', max_length=100)
    birthdate = forms.DateField(label='Birthdate', widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(label='Address', max_length=255)
    district = forms.CharField(label='District', max_length=100)