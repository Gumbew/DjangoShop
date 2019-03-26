from django import forms
from django.utils import timezone
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Username'
        self.fields['password'].label = 'Password'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('User with this login is not registered in the system!')
        user = User.objects.get(username=username)
        if user and not user.check_password(password):
            raise forms.ValidationError('Wrong password!')


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_check = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'password',
            'password_check',
            'email'
        ]

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Username'
        self.fields['password'].label = 'Password'
        self.fields['password_check'].label = 'Repeat password'
        self.fields['first_name'].label = 'First name'
        self.fields['last_name'].label = 'Last name'
        self.fields['email'].label = 'Your email'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        password_check = self.cleaned_data['password_check']
        email = self.cleaned_data['email']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('User with this login is already registered in the system!')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('User with this email address is already registered!')
        if password != password_check:
            raise forms.ValidationError('Your passwords do not match! Try again!')


class OrderForm(forms.Form):
    name = forms.CharField()
    last_name = forms.CharField(required=False)
    phone = forms.CharField()
    buying_type = forms.ChoiceField(widget=forms.Select(),
                                    choices=([("self-delivery", "self-delivery"), ("delivery", "delivery")]))
    date = forms.DateField(widget=forms.SelectDateWidget(), initial=timezone.now())
    address = forms.CharField(required=False)
    comments = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Name'
        self.fields['last_name'].label = 'Last name'
        self.fields['phone'].label = 'Phone'
        self.fields['phone'].help_text = 'Please enter valid phone number'
        self.fields['buying_type'].label = 'Buying type'
        self.fields['address'].label = 'Address'
        self.fields['address'].help_text = '*Address'
        self.fields['comments'].label = 'Comments'
        self.fields['date'].label = 'Date'
        self.fields['date'].help_text = 'Delivery date'

