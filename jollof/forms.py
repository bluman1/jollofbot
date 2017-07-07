from django import forms

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.ImageField()


class SellerLogo(forms.Form):
    logo = forms.ImageField()


class JollofImage(forms.Form):
    image = forms.ImageField()


class DelicacyImage(forms.Form):
    image = forms.ImageField()
