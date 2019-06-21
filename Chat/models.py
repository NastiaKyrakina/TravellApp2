from django.db import models
from django.contrib.auth.models import User
from Lib import FFD
from django.utils.translation import ugettext_lazy as _


class ChatManager(models.Manager):

    def users_chats(self, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return

        chats = self.filter(member__user=user)
        return chats

    def has_conversation(self, user, opponent):
        user_chat = self.filter(chat_type=Chat.P2P, member__user=user)
        conversation = user_chat.filter(member__user=opponent).first()
        return conversation


class MessageManager(models.Manager):

    def last_10_messages(self, chat, since=None):
        qs = self.filter(chat=chat).order_by('-date')
        if since:
            qs = qs.filter(date__lte=since)
        qs = qs[0:10]
        return qs


class Chat(models.Model):
    P2P = 0
    PRIVATE = 1
    PUBLIC = 2

    TYPE_CHATS = [
        (P2P, _('Talk')),
        (PRIVATE, _('Private')),
        (PUBLIC, _('Public')),
    ]

    name = models.CharField(max_length=25, blank=True)
    slug = models.SlugField(blank=True)
    chat_type = models.SmallIntegerField(choices=TYPE_CHATS, default=P2P)
    date_create = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to='chat_data/photo/', blank=True, null=True)

    members = models.ManyToManyField(User, through='Member')

    objects = models.Manager()
    chat_objects = ChatManager()

    def set_slug(self):
        self.slug = '%s_chat' % self.id

    def get_chat_title(self, username):
        if self.chat_type == Chat.P2P:
            title_set = self.name.split('|')
            if username == title_set[0]:
                title = title_set[1]
            else:
                title = title_set[0]
        else:
            title = self.name
        return title

    def get_image(self, user):
        if self.image:
            return self.image
        if self.chat_type == Chat.P2P:
            opponent = self.member_set.exclude(user=user).first()

            if opponent and opponent.user and opponent.user.userinfo:
                return opponent.user.userinfo.big_photo
        return None

    def save(self, *args, **kwargs):
        super(Chat, self).save(*args, **kwargs)
        self.set_slug()
        super(Chat, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def has_new_messages(self, user):
        last_mess = self.last_message()

        if last_mess and user != last_mess.user:
            return self.member_set.filter(user=user, last_visit__lt=last_mess.date).exists()
        return False

    def last_message(self):
        try:
            last_message = self.message_set.order_by('-date')[0]
        except IndexError:
            last_message = None
        return last_message

    def new_message(self, user_id):
        last_visit = self.member_set.get(user__id=1).last_visit
        new_message = self.objects.filter(message__date__gt=last_visit)
        return new_message

    def members(self):
        return self.member_set.all()

    def creator(self):
        creator = self.member_set.filter(status=Member.CREATOR).values('user').first()
        if creator:
            return creator['user']
        return None

    def is_creator(self, user):
        return True
        # return self.filter(status=Member.CREATOR, user=user).first()

    def is_multi_chat(self):
        return self.chat_type != Chat.P2P


class Member(models.Model):
    CREATOR = 1
    USER = 0

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    status = models.BooleanField(default=USER)
    last_visit = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s | %s" % (self.user.username, self.chat.name)

    def user_chat_title(self):
        return self.chat.get_chat_title(self.user.username)


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    message_object = MessageManager()
    objects = models.Manager()

    def __str__(self):
        return self.text[0:100]

    def save(self, *args, **kwargs):
        super(Message, self).save(*args, **kwargs)

    def has_files(self):
        return self.messageattachment_set.all()

    def get_images(self):
        return self.messageattachment_set.filter(type=FFD.IMAGE)

    def get_video(self):
        return self.messageattachment_set.filter(type=FFD.VIDEO)

    def get_audio(self):
        return self.messageattachment_set.filter(type=FFD.AUDIO)

    def get_files(self):
        return self.messageattachment_set.filter(type=FFD.FILES)


class MessageAttachment(models.Model):
    parent = models.ForeignKey(Message, on_delete=models.CASCADE)
    type = models.CharField(max_length=2,
                            choices=FFD.FILE_TYPE)
    file = models.FileField(upload_to='chat_data/files/',
                            blank=True)
