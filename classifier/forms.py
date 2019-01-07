from django import forms

class ArForm(forms.Form):
    article = forms.CharField(label='article', max_length=10000000000000000000000000000)