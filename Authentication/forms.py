from django import forms
import re
from UserProfile.models import User, UserInfo, UserExt
from django.utils.translation import ugettext_lazy as _

class AuthorizationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=30)
    password = forms.CharField(
        label='Passport',
        widget=forms.PasswordInput()
    )


class RegistrationForm(forms.Form):
    first_name = forms.CharField(label='First name',
                                 max_length=30,
                                 widget=forms.TextInput(attrs={
                                     'class': "form-control mb-2",
                                     'placeholder': _("First name")
                                 })

                                 )
    last_name = forms.CharField(label='Last name', max_length=30,
                                widget=forms.TextInput(attrs={
                                    'class': "form-control mb-2",
                                    'placeholder': _("Last name"),
                                }
                                ))

    username = forms.CharField(label='Username', max_length=30,
                               widget=forms.TextInput(attrs={
                                   'class': "form-control",
                                   'placeholder': _("Username"),
                               }
                               )
                               )
    email = forms.EmailField(label='Email',
                             widget=forms.EmailInput(attrs={
                                 'class': "form-control mb-2",
                                 'placeholder': _("Email"),
                             })
                             )
    password1 = forms.CharField(
        label='Passport',
        widget=forms.PasswordInput(attrs={
            'class': "form-control mb-2",
            'placeholder': _("Password"),
        })
    )
    password2 = forms.CharField(
        label='Passport (again)',
        widget=forms.PasswordInput(attrs={
            'class': "form-control mb-2",
            'placeholder': _("Confirm password"),
        })
    )

    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2:
                return password2
        raise forms.ValidationError(_('Passwords do not match'))

    def clean_username(self):
        username = self.cleaned_data['username']
        print(username)
        if not re.search(r'^\w+[\w_-]*$', username):
            raise forms.ValidationError(_('Username can only contain alphanumeric characters and the underscore.'))
        try:
            User.objects.get(username=username)

        except User.DoesNotExist:
            print('get')
            return username
        print('under')
        raise forms.ValidationError(_('Username is already taken.'), code='invalid')

    def save(self):

        new_user = UserExt.objects.create_user(
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1']
        )
        new_user.save()
        new_user_info = UserInfo(user=new_user)
        new_user_info.save()
        return new_user


class InformationForm(forms.ModelForm):

    class Meta:
        model = UserInfo
        exclude = ['user', 'registration', 'last_visit', 'virifield']

        GENDER_SELECT = (
            (0, 'male'),
            (1, 'female')
        )

        widgets = {
            'gender': forms.RadioSelect(choices=GENDER_SELECT, attrs={
                'class': 'custom-control-input',
                'title': _('choice gender'),
            }),
            'birthday': forms.DateInput(attrs={
                'class': 'form-control mb-2',
                'title': _('enter your birthday: day.month.year'),
                'placeholder': 'dd.mm.yyyy',
            }),
            'status': forms.Select(choices=UserInfo.STATUS_TYPE, attrs={
                'class': 'custom-select',
                'title': _("select you's status"),
            }),
            'phone_num': forms.TextInput(attrs={
                'class': 'form-control mb-2',
                'title': _("enter a phone number"),
            }),
            'country': forms.TextInput(attrs={
                'name': 'country',
                'required': True,
                'class': 'form-control mb-2',
                'placeholder': _('Country'),
                'title': _('Select country'),
                'maxlength': 30,
                'list': 'countries'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control mb-2',
                'title': _('Select city'),
                'placeholder': _('City'),
            }),
            'info': forms.Textarea(attrs=
            {
                'maxlength': 1000,
                'class': 'form-control mb-2',
                'rows': '4',
                'title': _('tell about yourself'),
                'placeholder': _('Hello everyone!'),
            }),
            'big_photo': forms.FileInput(attrs=
            {
                'class': 'invisible position-absolute',
                'required': False,
                'accept': 'image/*',
                'title': _('set main photo for you profile'),
            }),
       }

    def save(self, user):
        user_info = super(InformationForm, self).save(commit=False)
        user_info.user = user
        return user_info.save()