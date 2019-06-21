from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from model_utils import Choices
from Lib import FFD
from django.utils.translation import ugettext_lazy as _

class UserExt(User):
    class Meta:
        proxy = True

    def get_new_note_portion(self, since=None, limit=10):
        qs = self.note_set.order_by('-date_public')
        if since:
            qs = qs.filter(date_public__lte=since)
        qs = qs[0:limit]
        return qs

    def get_absolute_url(self):
        return reverse('home', args=[str(self.id)])

    def get_diary(self):
        active_diary = self.diary_set.filter(status=Diary.ACTIVE).first()
        if active_diary:
            return active_diary
        else:
            return self.diary_set.all().first()

    def has_diary(self):
        return self.diary_set.all().exists()

    # def has_adv(self):
    #     return self.house_set.all().exists()


class Country(models.Model):
    name = models.CharField(max_length=30)
    phone_code = models.CharField(max_length=4)

    def __str__(self):
        return self.name


class UserInfo(models.Model):

    TRAVEL = 'TR'
    SEARCH = 'SH'
    RENT_HOUSE = 'HH'
    UNDF = 'UF'
    STATUS_TYPE = Choices(
        (TRAVEL, _('Travelling')),
        (SEARCH, _('Find house')),
        (RENT_HOUSE, _('Rent a house')),
        (UNDF, _('Undefined')),
    )
    VERIFIED = 'VR'
    WAIT = 'WT'
    REJECT = 'RJ'
    STATUS_VRF = Choices(
        (VERIFIED, _('Сhecked')),
        (WAIT, _('Wait for check')),
        (REJECT, _('Denied')),
        (UNDF, _('Undefined')),
    )

    user = models.OneToOneField(User,
                                unique=True,
                                on_delete=models.CASCADE)
    gender = models.BooleanField(default=False)
    birthday = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=2,
                              choices=STATUS_TYPE,
                              default=UNDF)

    phone_num = models.CharField(max_length=12,
                                 blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    city = models.CharField(max_length=30,
                            blank=True)
    info = models.TextField(max_length=256,
                            blank=True)
    virifield = models.CharField(max_length=2,
                                 choices=STATUS_VRF,
                                 default=UNDF)
    big_photo = models.ImageField(upload_to='user_photo/',
                                  blank=True)

    def get_photo(self):
        if self.big_photo:
            return self.big_photo.url
        else:
            return '/static/images/DefaultAvatar.png'

    def __str__(self):
        return self.user.last_name + ' ' + self.user.first_name

class NoteManager(models.Manager):

    def get_queryset(self):
        return super(NoteManager, self).get_queryset().filter(deleted__isnull=True)


class NoteDeleteManager(models.Manager):

    def get_queryset(self):
        return super(NoteDeleteManager, self).get_queryset().filter(deleted__isnull=False).order_by('-deleted')


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000, blank=True)
    date_public = models.DateTimeField(auto_now_add=True)

    deleted = models.DateField(null=True, db_index=True)

    # note_objects = NoteManager()
    objects = NoteManager()
    note_delete_objects = NoteDeleteManager()

    def get_absolute_url(self):
        return reverse('note', args=[str(self.id)])

    def get_images(self):
        return self.attachment_set.filter(type=FFD.IMAGE)

    def get_video(self):
        return self.attachment_set.filter(type=FFD.VIDEO)

    def get_audio(self):
        return self.attachment_set.filter(type=FFD.AUDIO)

    def get_files(self):
        return self.attachment_set.filter(type=FFD.FILES)

    def is_bound(self):
        try:
            marker = self.marker
        except Marker.DoesNotExist:
            return False
        return marker

    def get_diary(self):
        try:
            marker = self.marker
        except Marker.DoesNotExist:
            return False
        return marker.diary


def get_upload_file_way(ftype):
    return 'user_files/%s/' % ftype


class Attachment(models.Model):
    parent = models.ForeignKey(Note, on_delete=models.CASCADE)
    type = models.CharField(max_length=2,
                            choices=FFD.FILE_TYPE)
    file = models.FileField(upload_to='user_files/all_files/',
                            blank=True)


def save_attach(files_dict, note, attachment_class):
    files = files_dict.getlist('images', None)
    for file in files:
        new_attachment = attachment_class(parent=note, file=file, type='IM')
        new_attachment.save()

    files = files_dict.getlist('video', None)
    for file in files:
        new_attachment = attachment_class(parent=note, file=file, type='VD')
        new_attachment.save()

    files = files_dict.getlist('audio', None)
    for file in files:
        new_attachment = attachment_class(parent=note, file=file, type='AU')
        new_attachment.save()

    files = files_dict.getlist('files', None)
    for file in files:
        new_attachment = attachment_class(parent=note, file=file, type='FL')
        new_attachment.save()


class Diary(models.Model):
    ACTIVE = 0
    FROZEN = 1
    FINISH = 2

    STATUS_TYPE = (
        (ACTIVE, 'active'),
        (FROZEN, 'frozen'),
        (FINISH, 'finish')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    about = models.TextField(max_length=1000)
    date_start = models.DateField(auto_now_add=True)
    date_finish = models.DateField(blank=True, null=True)
    status = models.SmallIntegerField(choices=STATUS_TYPE, default=ACTIVE)
    photo = models.ImageField(upload_to='diary_photo/', blank=True)

    def is_active(self):
        return not (self.status)

    def is_frozen(self):
        return self.status == Diary.FROZEN

    def is_finish(self):
        return self.status == Diary.FINISH

    def get_absolute_url(self):
        return reverse('user_profile.diary_page', args=[str(self.id)])


class Marker(models.Model):
    note = models.OneToOneField(Note,
                                unique=True,
                                on_delete=models.CASCADE)
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)