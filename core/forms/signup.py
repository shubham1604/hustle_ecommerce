from django import forms
from django.contrib.auth.forms import UserCreationForm
from core.models import MyUser
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError


class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True,widget = forms.TextInput(attrs={'class':'form-control col-lg-6 offset-lg-3  mb-4', 'placeholder':'First Name'}))
    last_name = forms.CharField(max_length=30, required=True,widget = forms.TextInput(attrs={'class':'form-control col-lg-6 offset-lg-3  mb-4', 'placeholder':'Last Name'}))
    email = forms.EmailField(max_length=254,required=True ,help_text='Required. Inform a valid email address.', widget = forms.TextInput(attrs={'class':'form-control col-lg-6 offset-lg-3  mb-4', 'placeholder':'Email'}))
    password1 = forms.CharField(
        required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class':'form-control col-lg-6 offset-lg-3  mb-4', 'placeholder':'Password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class':'form-control col-lg-6 offset-lg-3  mb-4', 'placeholder':'Confirm Password'}),
        strip=False,
        help_text= "Enter the same password as before, for verification."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs['autofocus'] = True


    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if MyUser.objects.filter(email=email).exists():
            self.add_error("email", "Email Already Exists")
        return email


    class Meta:
        model = MyUser
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2',)
