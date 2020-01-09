from django import forms

from controller.models import *


class CaptureConfigForm(forms.Form):

    description = forms.CharField(label='Description', max_length=100, widget=forms.TextInput(attrs={'class': 'input-left-100'}))
    iso = forms.ChoiceField(choices=ISOS, label="Iso", widget=forms.Select(), required=True)
    aperture = forms.ChoiceField(choices=APERTURES, label="Aperture", widget=forms.Select(), required=True)
    exposure = forms.ChoiceField(choices=EXPOSURES, label="Exposure", widget=forms.Select(), required=False)
    bulb_time = forms.IntegerField(max_value=7200, label="Bulb", widget=forms.TextInput(attrs={'class': 'input-left-100'}), required=False, initial=0)
    image_format = forms.ChoiceField(choices=FORMAT_TYPES, label="Image-Format", widget=forms.Select(), required=True)

    def __init__(self, *args, **kwargs):
        super(CaptureConfigForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['style'] = 'width:180px;'
        self.fields['iso'].widget.attrs['style'] = 'width:80px;'
        self.fields['aperture'].widget.attrs['style'] = 'width:80px;'
        self.fields['exposure'].widget.attrs['style'] = 'width:80px;'
        self.fields['bulb_time'].widget.attrs['style'] = 'width:80px;'
        self.fields['image_format'].widget.attrs['style'] = 'width:180px;'

    def get_form(self, **kwargs):
        form = CaptureConfigForm()

        if kwargs is not None:
            for key, value in kwargs.items():
                form.base_fields[key].initial = value

        return form
