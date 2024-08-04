from django import forms

class PdfExtractForm(forms.Form):
    file = forms.FileField()
