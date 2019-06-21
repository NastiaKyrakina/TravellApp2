from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, QueryDict, HttpRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.db.models import Q

from UserProfile.models import UserExt, Country
from .models import House, HousePhoto, Booking, MAX_USER_HOUSES
from .form import HouseForm, PhotoForm, SearchHousesForm, RateForm, BookingForm
from Chat.forms import ChatMember
from datetime import datetime
from Lib import FileFormats, page_revisor

from django.db.models import Avg


def rate_create(request):

    user = UserExt.objects.get(pk=request.user.pk)

    if request.method == 'POST' and 'house' in request.POST:
        house = get_object_or_404(House, id=request.POST['house'])
        form_rate = RateForm(request.POST)
        if form_rate.is_valid():
            print(user)
            print(house)
            rate = form_rate.save(user, house)
            if request.is_ajax():
                return render(request,
                              'HouseSerch/includes/rate-block.html',
                              {
                                  'rate': rate,
                               }
                              )
            return HttpResponseRedirect('house/%s/' % house.pk)
    else:
        form_rate = RateForm()

    return render(request, 'HouseSerch/includes/form_rate_block.html', {
        'form_rate': form_rate,
    })


def booking_create(request):
    user = UserExt.objects.get(pk=request.user.pk)

    if request.method == 'POST' and 'house' in request.POST:
        house = get_object_or_404(House, id=request.POST['house'])
        form_booking = BookingForm(request.POST)
        if form_booking.is_valid():
            book = form_booking.save(user, house)
            if request.is_ajax():
                return render(request,
                              'HouseSerch/create_booking_form.html',
                              {
                                  'book': book,
                              }
                              )
            return HttpResponseRedirect('house/%s/' % house.pk)
    else:
        form_booking = BookingForm()

    return render(request, 'HouseSerch/create_booking_form.html', {
        'form_booking': form_booking,
        'is_creating': True,
    })

def main_search(request):
    if 'text' in request.GET:
        print(request.GET['text'])

    return HttpResponseRedirect('/house/')


def user_houses(request):
    if 'user' in request.GET:
        user = get_object_or_404(UserExt, id=request.GET['user'])
        houses = House.objects.filter(owner=user)


def house_search_page(request):
    if 'reset' in request.GET:
        return HttpResponseRedirect(request.path)

    request.META['QUERY_STRING'] = \
        page_revisor.remove_page(request.META['QUERY_STRING'])

    houses = House.objects.all()
    form_search = SearchHousesForm()

    if 'text' in request.GET and request.GET['text']:
        houses = House.objects.ft_search(request.GET.dict()['text'])

    if 'country' in request.GET:

        form_search = SearchHousesForm(request.GET)

        if form_search.is_valid():
            dict = form_search.get_only_full()

            if len(dict):
                houses = House.objects.multi_search(houses, dict)


    context = {
        'form_search': form_search,
    }

    if houses:

        message = _("Result: ") + str(houses.count())

        if 'sort' in request.GET:
            houses = House.objects.sorting(houses, request.GET['sort'])

        paginator = Paginator(houses, 4)
        page = request.GET.get('page')

        try:
            houses_page = paginator.page(page)
        except PageNotAnInteger:
            houses_page = paginator.page(1)
        except EmptyPage:
            houses_page = paginator.page(paginator.num_pages)

        context['houses'] = houses_page

    else:
        message = _("No result :(")

    context['message'] = message

    return render(request, 'HouseSerch/house_search.html', context)


def house_page(request, house_id):
    house = get_object_or_404(House, id=house_id)
    is_owner = (request.user == house.owner)
    type = house.HOUSE_TYPE[house.type]
    raiting = house.rate_set.aggregate(Avg('value'))
    contact_form = ChatMember(initial={'members': house.owner.username})

    try:
        book = Booking.objects.get(user=request.user.id)
    except Booking.DoesNotExist:
        book = ''

    data = {
        'type': type,
        'house': house,
        'is_owner': is_owner,
        'raiting': raiting['value__avg'],
        'members_form': contact_form,
        'book': book
    }
    return render(request, 'HouseSerch/house_page.html', data)


@login_required
def house_admin(request, house_id):
    house = House.objects.get(id=house_id)

    rating = house.rate_set.filter(date_public__year=2018)
    booking = house.booking_set.all().order_by('start')
    rate_val = []
    counter = 0
    sum = 0
    all = 0
    for i in range(1, 13):
        rate = rating.filter(date_public__month=str(i))
        value = rate.aggregate(Avg('value'))
        print(value['value__avg'])
        count = rate.count()
        if value['value__avg']:
            sum = sum + value['value__avg']
            counter = counter + count
            all = sum / counter
        rate_val.append(all)

    return render(request,
                  'HouseSerch/admin_house_page.html', {
                      'house': house,
                      'rating': rating,
                      'rates_val': rate_val,
                      'booking': booking,
                  })


@login_required
def control_room(request):
    houses = House.objects.filter(owner=request.user.pk)
    return render(request,
                  'HouseSerch/control_room.html', {
                      'houses': houses,
                  })
@login_required
def house_add_page(request):
    user = UserExt.objects.get(pk=request.user.pk)

    if user.house_set.count() == MAX_USER_HOUSES:
        return render(request, 'HouseSerch/limit_house.html', {user: user})

    errors_file_type = []

    if request.method == 'POST':
        form_house = HouseForm(request.POST)
        form_photo = PhotoForm(request.POST, request.FILES)
        if form_house.is_valid() and form_photo.is_valid():
            errors_file_type = FileFormats.handle_uploaded_file(request.FILES)
            if not errors_file_type:
                new_house = _home_save(request, form_house, user)
                return HttpResponseRedirect('/house/%s/' % new_house.id)
        else:
            print(form_house.errors);
            print(form_house.cleaned_data['country']);
    else:
        form_house = HouseForm()
        form_photo = PhotoForm()

    return render(request,
                  'HouseSerch/add_house.html',
                  {'form_house': form_house,
                   'form_photo': form_photo,
                   'is_creating': True,
                   'errors_type': errors_file_type,
                   })


def _home_save(request, form_house, user):
    new_house = form_house.save(user)
    files = request.FILES.getlist('image', None)
    for file in files:
        new_house_photo = HousePhoto(house=new_house, image=file)
        new_house_photo.save()
    return new_house


def house_edit_page(request, house_id):
    house = get_object_or_404(House, id=house_id)
    user = UserExt.objects.get(pk=request.user.pk)

    if user != house.owner:
        return Http404

    errors_file_type = []
    if request.method == 'POST':
        form_house = HouseForm(request.POST, instance=house)
        form_photo = PhotoForm(request.POST, request.FILES)
        if form_house.is_valid() and form_photo.is_valid():
            errors_file_type = FileFormats.handle_uploaded_file(request.FILES)
            if not errors_file_type:
                new_house = _home_save(request, form_house, user)
                return HttpResponseRedirect('/house/%s/' % new_house.id)
    else:
        form_house = HouseForm(instance=house)
        form_photo = PhotoForm()

    return render(request,
                  'HouseSerch/add_house.html',
                  {'form_house': form_house,
                   'form_photo': form_photo,
                   'house': house,
                   'errors_type': errors_file_type,
                   })


def house_delete(request):
    if request.method == 'POST':
        house = House.objects.get(pk=int(QueryDict(request.body).get('housepk')))
        if request.user == house.owner:
            house.deleted = datetime.now()
            house.save()
            response_data = {}
            response_data['msg'] = 'Post was deleted.'
            return JsonResponse(response_data)

    return JsonResponse({"msg": "this isn't happening"})


def users_house(request, user_id):
    user = get_object_or_404(UserExt, id=user_id)
    houses = user.house_set.all()
    context = {
        'houses': houses,
        'user': user,
    }

    return render(request, 'HouseSerch/user_houses.html', context)


def change_status(request):
    status = 'fail'

    if request.method == 'POST':
        house_id = request.POST['housepk']

        try:
            house = House.objects.get(id=house_id)
            if request.user == house.owner:
                house.activity = not house.activity
                house.save()
                status = house.activity

        except House.DoesNotExist:
            status = 'fail'
    return JsonResponse({'status': status})
