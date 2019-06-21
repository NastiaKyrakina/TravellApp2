from django import forms
from django.db.models import Max
from django.utils.translation import ugettext_lazy as _

import re
from UserProfile.models import Country
from HouseSearch.models import House, \
    HousePhoto, Rate, Booking, MAX_PRICE, MAX_ROOMS, MAX_SLEEPER, SORT_DICT

from Lib.convertion import from_dict_to_list
from datetime import datetime, date

class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ['title', 'country', 'city', 'address', 'type',
                  'rooms', 'sleeper', 'price', 'activity', 'about']

        widgets = {
            'title': forms.TextInput(attrs={

                'required': True,
                'class': 'form-control mb-2',
                'placeholder': _('Title'),
                'title': _('Enter title of advertisement'),
                'maxlength': 100,

            }),

            'country': forms.TextInput(attrs={
                'name': 'city',
                'class': 'form-control mb-2',
                'placeholder': _('Country'),
                'title': _('Select a country'),
                'list': 'countries',
            }),

            # pattern = "[\+]\d{1}\s[\(]\d{3}[\)]\s\d{3}[\-]\d{2}[\-]\d{2}"
            'city': forms.TextInput(attrs={
                'name': 'city',
                'class': 'form-control mb-2',
                'placeholder': _('City'),
                'title': _('Enter city: only alphabet character valid'),
                'maxlength': 40,
                # 'pattern': '[A-Za-zА-ЯЙйЁёЫыъьІіЄєЇї]*[ -`][A-Za-zА-ЯЙйЁёЫыъьІіЄєЇї]*',

            }),
            'address': forms.TextInput(attrs={
                'name': 'Address',
                'class': 'form-control mb-2',
                'placeholder': _('Street, 1, 1'),
                'full_title': _('Enter address: Street name, House number, Apartment number'),
                'short_title': _('Enter address: Street name, House number'),
                'title': _('Enter address: Street name, House number'),
                'maxlength': 100,

            }),
            'type': forms.Select(choices=House.HOUSE_TYPE,
                                 attrs={
                                     'class': 'form-control mb-2',
                                     'name': 'type',
                                     'title': 'Select house-type',
                                 }),
            'rooms': forms.NumberInput(attrs={
                'name': 'rooms',
                'class': 'form-control mb-2',
                'title': _('Enter rooms count'),
                'min': 1,
                'max': MAX_ROOMS,
            }),

            'price': forms.NumberInput(attrs={
                'name': 'price',
                'class': 'form-control',
                'title': _('Enter rental price per day'),
                'value': 10,
                'min': 1,
                'max': MAX_PRICE,
                'step': 1,
            }),
            'sleeper': forms.NumberInput(attrs={
                'name': 'sleeper',
                'class': 'form-control mb-2',
                'required': False,
                'title': _('Enter sleeper count'),
                'min': 1,
                'max': MAX_SLEEPER,

            }),

            'about': forms.Textarea(attrs={
                'name': 'about',
                'class': 'form-control mb-2',
                'title': _('Tell about house'),
                'placeholder': _('Tell about house...'),
            }),

            'activity': forms.CheckboxInput(attrs={
                'class': 'custom-control-input',
            }),
        }

    def clean_rooms(self):
        rooms = self.cleaned_data['rooms']
        if rooms <= 0 or rooms > MAX_ROOMS:
            raise forms.ValidationError(_('Uncorrected ROOMS count. Must be value from 1 to %s' % MAX_ROOMS),
                                        code='uncorrect_diapazone')
        return rooms

    def clean_sleeper(self):
        sleeper = self.cleaned_data['sleeper']
        if sleeper <= 0 or sleeper > MAX_SLEEPER:
            raise forms.ValidationError(_('Uncorrected SLEEPER count. Must be value from 1 to %s' % MAX_SLEEPER),
                                        code='uncorrect_diapazone')
        return sleeper

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0 or price > MAX_PRICE:
            raise forms.ValidationError(_('Uncorrected PRICE. Must be value from 1 to %s' % MAX_PRICE),
                                        code='uncorrect_diapazone')
        return price


    def save(self, user):
        house = super(HouseForm, self).save(commit=False)
        house.owner = user
        house.save()
        return house


class PhotoForm(forms.ModelForm):
    class Meta:
        model = HousePhoto
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs=
                                     {'name': 'photo',
                                      'class': 'house-edit-images invisible position-absolute',
                                      'multiple': True,
                                      'required': False,
                                      'accept': 'image/*'})
        }


SORTED_TYPE = from_dict_to_list(SORT_DICT)


class SearchHousesForm(forms.Form):
    country = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'name': 'country',
            'required': False,
            'placeholder': _('Country'),
            'title': _('Choice country for search'),
            'maxlength': 30,
            'list': 'countries',
            'class': 'form-control mb-2'
        })
    )

    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'name': 'city',
            'required': False,
            'placeholder': _('City'),
            'title': _('Enter city name for search'),
            'maxlength': 40,
            'class': 'form-control mb-2'
        })
    )

    type = forms.MultipleChoiceField(
        required=False,
        choices=House.HOUSE_TYPE,
        widget=forms.CheckboxSelectMultiple(attrs={
            'name': 'type',
            'required': False,
            'checked': True,
            'title': _('Choice house-types for search'),
        })
    )

    req_max_price = 100
    # House.objects.aggregate(Max('price'))['price__max']

    min_price = forms.DecimalField(
        label='From',
        required=False,
        initial=0.00,
        widget=forms.NumberInput(attrs={
            'name': 'min_price',
            'required': False,
            'title': _('Enter minimum price'),
            'min': 0,
            'max': req_max_price,
            'class': 'form-control'
        })
    )
    max_price = forms.DecimalField(
        label='To',
        required=False,
        initial=req_max_price,
        widget=forms.NumberInput(attrs={
            'name': 'max_price',
            'required': False,
            'title': _('Enter maximum price'),
            'min': 0,
            'max': req_max_price,
            'class': 'form-control'
        })
    )
    rooms = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'name': 'rooms',
            'required': False,
            'placeholder': '1',
            'title': _('Enter rooms count'),
            'min': 1,
            'max': 100,
            'class': 'form-control'
        })
    )
    # House.objects.aggregate(Max('rooms'))['rooms__max'],
    sleeper = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'name': 'sleeper',
            'required': False,
            'placeholder': '1',
            'title': _('Enter sleeper count'),
            'min': 1,
            'max': 100,
            'class': 'form-control'
        })

    )
    # House.objects.aggregate(Max('sleeper'))['sleeper__max'],
    active = forms.BooleanField(
        label='Only active',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'name': 'active',
            'required': False,
            'title': _('Search only active advertisement')
        })
    )
    #
    public = forms.DateField(
        required=False,
        initial=date(2018, 1, 1),
        widget=forms.SelectDateWidget(
            years=range(2017, datetime.now().year + 1),
            attrs={

            'name': 'public',
            'required': False,
                'title': _('Search advertisement populated after this date'),
            'class': 'custom-select col-3'
        })

    )

    text = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={
            'name': 'text',
            'required': False,
            'id': 'hide-text',
        })

    )

    sort = forms.ChoiceField(
        choices=SORTED_TYPE,
        required=False,
        widget=forms.Select(attrs={
            'name': 'sort',
            'required': False,
            'class': 'select_sort pull-right text-right',
            'title': _('Select sorting option'),
        })
    )

    def get_only_full(self):
        """Очистка списка значений полей от пустых полей"""
        dict = self.cleaned_data.copy()

        for key in self.cleaned_data:
            if not (dict[key]) and key != 'type':
                del dict[key]
        return dict


class RateForm(forms.ModelForm):
    class Meta:
        model = Rate
        fields = ['comment', 'value']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control mb-1',
                'placeholder': _('Leave your comment here'),
                'rows': '3'
            }),
            'value': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 5,
                'min': 1,
                'max': 5,
            }),
        }
    def save(self, user, house, *args, **kwargs):
        new_rate = Rate(comment=self.cleaned_data['comment'],
                        value=self.cleaned_data['value'])
        new_rate.user = user
        new_rate.house = house

        new_rate.save()
        return new_rate


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start', 'people', 'comment', 'phone_num']
        widgets = {
            'start': forms.TextInput(attrs={
                'class': "datepicker-here form-control",
                'data-position': "right top",
                'data-multiple-dates-separator': " - ",
                'data-range': "true",
            }),
            'people': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 1,
                'min': 1,
                'max': 100,
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Leave here your remarks and wishes'),
            }),
            'phone_num': forms.TextInput(attrs={
                'class': 'form-control mb-2',
                'title': _("enter a phone number"),
            }),

        }

    def save(self, user, house, *args, **kwargs):
        rg = self.cleaned_data['start'].split(' - ')
        start_arr = rg[0].split('/')
        end_arr = rg[1].split('/')

        start = date(int(start_arr[2]), int(start_arr[0]), int(start_arr[1]))
        end = date(int(end_arr[2]), int(end_arr[0]), int(end_arr[1]))

        new_booking = Booking(start=start,
                              end=end,
                              people=self.cleaned_data['people'],
                              comment=self.cleaned_data['comment'],
                              phone_num=self.cleaned_data['phone_num'],
                              )
        new_booking.user = user
        new_booking.house = house

        new_booking.save()
        return new_booking
