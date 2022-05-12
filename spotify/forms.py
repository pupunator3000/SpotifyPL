from django import forms

class NameForm(forms.Form):
    user_playlists = forms.CharField(label='Enter playlist number', max_length=3)
