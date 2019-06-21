from django.contrib import admin

from HouseSearch.models import House
from .models import UserInfo, Country


# Register your models here.
@admin.register(UserInfo)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'birthday', 'gender', 'phone_num', 'country', 'virifield')
    list_filter = ('virifield',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # when editing an object
            return ['user', 'birthday', 'gender', 'status', 'phone_num', 'country', 'city', 'info', 'big_photo']
        return self.readonly_fields


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    pass
