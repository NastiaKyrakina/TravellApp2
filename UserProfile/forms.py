from django import forms
from django.utils.translation import ugettext_lazy as _

from UserProfile.models import *

from datetime import datetime


class VerificationSendForm(forms.Form):
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'id': 'id_message',
            'class': 'form-control mb-3',
            'maxlength': 1000,
            'rows': False,
            'cols': False,
        })
    )
    image1 = forms.ImageField(
        label='image1',
        required=False,
        widget=forms.FileInput(attrs={
            'id': 'inputGroupImage1',
            'accept': 'image/*',
            'class': 'custom-file-input',
        }),
    )
    image2 = forms.ImageField(
        label='image2',
        required=False,
        widget=forms.FileInput(attrs={
            'id': 'inputGroupImage2',
            'accept': 'image/*',
            'class': 'custom-file-input',
        }),
    )




class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        exclude = ['user', 'date_public', 'deleted']

        widgets = {
            'text': forms.Textarea(attrs={'name': 'text',
                                          'id': 'id_text',
                                          'maxlength': 1000,
                                          'class': 'form-control h-100',
                                          'rows': False,
                                          'cols': False,
                                          'style': False,
                                          }),
        }


class AttachmentForm(forms.Form):
    images = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'name': 'photo',
                                      'multiple': True,
                                      'class': 'file invisible position-absolute',
                                      'required': False,
                                      'accept': 'image/*'})
    )

    video = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'name': 'video',
                                      'multiple': False,
                                      'class': 'file invisible position-absolute',
                                      'required': False,
                                      'accept': 'video/*'})
    )

    audio = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'name': 'audio',
                                      'multiple': True,
                                      'class': 'file invisible position-absolute',
                                      'required': False,
                                      'accept': 'audio/*'})
    )

    files = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'name': 'files',
                                      'class': 'file invisible position-absolute',

                                      'required': False,
                                      'multiple': True,
                                      })
    )


class DiaryForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ['title', 'about', 'date_finish', 'photo']

        widgets = {
            'title': forms.TextInput(attrs=
            {
                'class': 'form-control mb-2',
            }),
            'about': forms.Textarea(attrs=
            {
                'maxlength': 1000,
                'class': 'form-control mb-2',
            }),
            'date_finish': forms.DateInput(attrs=
            {
                'class': 'form-control mb-2',
                'placeholder': 'YYYY-MM-DD',
            }),
            'photo': forms.FileInput(attrs=
            {
                'class': 'invisible position-absolute',
                'required': False,
                'accept': 'image/*'
            }),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 100:
            raise forms.ValidationError(_('Title must be no longer than 100 characters'))
        elif len(title) < 10:
            raise forms.ValidationError(_('Title must be longer than 10 characters.'))
        return title

    def clean_date_finish(self):
        date_finish = self.cleaned_data['date_finish']
        if date_finish <= datetime.now().date():
            raise forms.ValidationError(_('Uncorrected diary finish date. Finish date must be later than start date.'),
                                        code='uncorrect_diapazone')
        return date_finish

    def clean_about(self):
        about = self.cleaned_data['about']
        if len(about) > 1000:
            raise forms.ValidationError(_('Description must be no longer than 1000 characters'))
        elif len(about) < 100:
            raise forms.ValidationError(_('Description must be longer than 100 characters.'))
        return about

    def save(self, user, *args, **kwargs):
        diary = super(DiaryForm, self).save(commit=False)
        diary.user = user
        diary.save()
        return diary


class MarkerForm(forms.ModelForm):
    class Meta:
        model = Marker
        fields = ['lat', 'lng']
        widgets = {
            'lat': forms.TextInput(attrs={
                'class': 'form-control mb-1',
                'required': False,
            }),
            'lng': forms.TextInput(attrs={
                'class': 'form-control mb-1',
                'required': False,
            })
        }