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


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label='Mật khẩu hiện tại',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control password-field',
            'placeholder': 'Nhập mật khẩu hiện tại',
            'autocomplete': 'current-password',
            'id': 'old_password'
        })
    )
    new_password = forms.CharField(
        label='Mật khẩu mới',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control password-field',
            'placeholder': 'Nhập mật khẩu mới',
            'autocomplete': 'new-password',
            'id': 'new_password'
        })
    )
    confirm_new_password = forms.CharField(
        label='Xác nhận mật khẩu mới',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control password-field',
            'placeholder': 'Nhập lại mật khẩu mới',
            'autocomplete': 'new-password',
            'id': 'confirm_password'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.required = True
            field.error_messages = {
                'required': 'Vui lòng nhập đầy đủ thông tin'
            }

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password and confirm_new_password:
            if new_password != confirm_new_password:
                raise forms.ValidationError("Mật khẩu mới và xác nhận mật khẩu không khớp.")
            
            if len(new_password) < 8:
                raise forms.ValidationError("Mật khẩu mới phải có ít nhất 8 ký tự.")
            
            if not any(char.isdigit() for char in new_password):
                raise forms.ValidationError("Mật khẩu mới phải chứa ít nhất một số.")
            
            if not any(char.isupper() for char in new_password):
                raise forms.ValidationError("Mật khẩu mới phải chứa ít nhất một chữ hoa.")

        return cleaned_data
