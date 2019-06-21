from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse

from Authentication.forms import *
from UserProfile.models import UserExt, Country

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _


def login_page(request):
    """"авторизация пользователя"""
    errors = []
    if request.method == 'POST':
        form = AuthorizationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/user/%s' % user.pk)
                else:
                    errors += [_("disabled account!")]
            else:
                errors += [_("Invalid username or password!")]
    else:
        form = AuthorizationForm()

    return render(request,
                  'Registration/authorization_page.html',
                  {'form': form,
                   'errors': errors,
                  })


def logout_page(request):
    """выход из аккаунта"""
    logout(request)
    return HttpResponseRedirect('/reg/login/')


def registration_page(request):
    """регистрация"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/reg/login/')
        else:
            print(form.errors)
    else:
        form = RegistrationForm()
    return render(request, 'Registration/registration_page.html', {'form': form})


@login_required
def information_page(request):
    """информация о ползователе"""
    try:
        user_info = UserInfo.objects.get(user=request.user)
    except UserInfo.DoesNotExist:
        user_info = None

    if request.method == 'POST':
        if user_info:
            form = InformationForm(request.POST, request.FILES, instance=user_info)
        else:
            form = InformationForm(request.POST, request.FILES)
        print(form.is_valid())
        print(form.errors)
        if form.is_valid():
            form.save(request.user)
            return HttpResponseRedirect('/user/%s/' % request.user.pk)
        else:
            return render(request, 'Registration/user_info_page.html', {'form': form})

    else:
        if user_info:
            form = InformationForm(instance=user_info)
        else:
            form = InformationForm()
    return render(request, 'Registration/user_info_page.html', {'form': form})


def ajax_load_countries(request):
    if 'qc' in request.GET:
        qc = request.GET['qc']
        countries = Country.objects.all()
        dictionaries = []
        for country in countries:
            country_json = {}
            country_json['name'] = country.name
            country_json['value'] = country.pk
            if qc == '2':
                country_json['phone_code'] = country.phone_code
            dictionaries.append(country_json)

        return JsonResponse({'dict': dictionaries})
    return HttpResponse('false')
