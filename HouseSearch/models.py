from django.db import models
from django.contrib.auth.models import User
from model_utils import Choices
from UserProfile.models import Country
from os import path


from django.urls import reverse
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.utils.translation import ugettext_lazy as _
from datetime import datetime

# 'key' - 'for user' - 'sort type'
SORT_DICT = {
    '0': (_('Newest'), '-date_public'),
    '1': (_('Highest rated'), '-rating'),
    '2': (_('Price High-Low'), '-price'),
    '3': (_('Price Low-High'), 'price'),
}


def get_sentinel_country():
    return Country.objects.get_or_create(name='deleted')[0]


class HouseManager(models.Manager):

    def get_queryset(self):
        return super(HouseManager, self).get_queryset().filter(deleted__isnull=True)

    def ft_search(self, text):
        query_world = [world for world in text.split(' ') if world]

        if not query_world:
            return None

        s_title = SearchVector('title')
        s_country = SearchVector('country__name')
        s_city = SearchVector('city')
        s_about = SearchVector('about')

        qfilter = SearchQuery(query_world[0])

        if len(query_world) > 1:
            for q in query_world:
                qfilter |= SearchQuery(q)

        houses = House.objects. \
            annotate(search=s_title + s_country + s_city + s_about). \
            filter(search=qfilter).order_by('-date_public')

        print(houses)
        return houses

    def multi_search(self, houses, kwargs):
        print(houses)
        print(kwargs)
        if 'min_price' in kwargs:
            houses = houses.filter(price__gte=kwargs['min_price'])
        if 'max_price' in kwargs:
            houses = houses.filter(price__lte=kwargs['max_price'])
        if 'country' in kwargs:
            houses = houses.filter(country__name=kwargs['country'])
        if 'type' in kwargs:
            print(kwargs['type'])
            for type in House.HOUSE_TYPE:
                if not (type[0] in kwargs['type']):
                    houses = houses.exclude(type=type[0])

        if 'city' in kwargs:
            houses = houses.filter(city=kwargs['city'])
        if 'rooms' in kwargs:
            houses = houses.filter(rooms=kwargs['rooms'])
        if 'sleeper' in kwargs:
            houses = houses.filter(sleeper=kwargs['sleeper'])
        if 'public' in kwargs:
            houses = houses.filter(date_public__gt=kwargs['public'])
        if 'active' in kwargs:
            houses = houses.filter(activity=True)

        return houses

    def sorting(self, houses, sort_option):
        if sort_option in SORT_DICT.keys():
            print('here')
            houses = houses.order_by(SORT_DICT[sort_option][1])
        return houses


class HouseDeleteManager(models.Manager):

    def get_queryset(self):
        return super(HouseDeleteManager, self).get_queryset().filter(deleted__isnull=False).order_by('-deleted')


MAX_USER_HOUSES = 20
MAX_PRICE = 999.99
MAX_ROOMS = 50
MAX_SLEEPER = 100

class House(models.Model):

    PRIVATE_HOUSE = 'PH'
    APARTMENT = 'AP'
    VILLA = 'VL'
    BUNGALOW = 'BN'
    COTTAGE = 'CT'

    HOUSE_TYPE = Choices(
        (PRIVATE_HOUSE, _('Private house')),
        (APARTMENT, _('Apartment')),
        (VILLA, _('Villa')),
        (BUNGALOW, _('Bungalow')),
        (COTTAGE, _('Cottage')),
    )
    """Owner user"""
    owner = models.ForeignKey(User, on_delete='Cascade')

    title = models.CharField(max_length=100, blank=True)

    """Piece of address"""
    country = models.ForeignKey(Country, on_delete=models.SET(get_sentinel_country))
    city = models.CharField(max_length=40)
    address = models.CharField(max_length=100)

    """Describe house"""
    type = models.CharField(max_length=2, choices=HOUSE_TYPE, default=PRIVATE_HOUSE)
    rooms = models.SmallIntegerField(default=1)
    sleeper = models.SmallIntegerField(default=1)
    about = models.TextField(max_length=500)

    price = models.DecimalField(decimal_places=2, max_digits=10)

    activity = models.BooleanField(default=True)
    date_public = models.DateField(auto_now_add=True)
    rating = models.DecimalField(decimal_places=1, max_digits=3, default=0)
    deleted = models.DateField(null=True, blank=True, db_index=True)

    objects = HouseManager()
    house_delete_objects = HouseDeleteManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('house', args=[str(self.id)])

    def get_images(self):
        return self.housephoto_set.all()

    def main_image(self):
        main_image = self.housephoto_set.first()
        if main_image:
            return main_image.image.url
        return None

    def count_rating(self):
        return self.rate_set.aggregate(models.Count('id'))['id__count']

    def cant_rate(self, user):
        now = datetime.now()
        self.rate_set.filter(user=user).values('date_public')

class HousePhoto(models.Model):
    house = models.ForeignKey(House, on_delete='Cascade')
    image = models.ImageField(upload_to='house_data/photo/', blank=True)

    def __str__(self):
        return self.image.path

    def get_filename(self):
        return path.basename(self.image.name)


class Rate(models.Model):
    user = models.ForeignKey(User, on_delete='Cascade')
    house = models.ForeignKey(House, on_delete='Cascade')
    value = models.PositiveSmallIntegerField()
    comment = models.TextField(max_length=1000)
    date_public = models.DateField(auto_now=True)
    correct = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.user.username + ' | ' + self.house.title

    def save(self, *args, **kwargs):
        super(Rate, self).save(*args, **kwargs)
        rate_val = Rate.objects.filter(house__id=self.house_id). \
            aggregate(models.Avg('value'))
        self.house.rating = rate_val['value__avg']
        self.house.save()


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete='Cascade')
    house = models.ForeignKey(House, on_delete='Cascade')
    start = models.TextField(max_length=60)
    end = models.TextField(max_length=60)
    people = models.PositiveIntegerField(default=1)
    comment = models.TextField(max_length=300, blank=True)
    phone_num = models.CharField(max_length=12,
                                 blank=True)

    def __str__(self):
        return self.user.username + ' | ' + self.house.title


class Advertising(models.Model):
    client = models.TextField(max_length=60)
    title = models.ForeignKey(House, on_delete='Cascade')
    href = models.TextField(max_length=400)
    photo = models.ImageField(upload_to='advertising/photo/', blank=True)
    start = models.DateTimeField(auto_now=True)
    end = models.DateTimeField()
