from django import forms


class CreatePersonForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email_address = forms.CharField()
    password = forms.CharField()
    password_2 = forms.CharField()
