from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, QueryDict, HttpRequest
from django.contrib.auth.decorators import login_required
from UserProfile.models import UserExt, save_attach
from .models import Chat, Message, Member, MessageAttachment
from UserProfile.forms import AttachmentForm
from .forms import MessageForm, ChatForm, ChatMember
from django.utils.safestring import mark_safe
import json
from datetime import datetime
from Lib.FileFormats import handle_uploaded_file


def add_members(request, chat_slug):
    context = {
        'status': 'success',
    }
    chat = get_object_or_404(Chat, slug=chat_slug)
    if not chat.is_creator(request.user):
        return Http404
        # fix this

    if request.method == 'POST':
        members_form = ChatMember(request.POST)
        if members_form.is_valid():
            members_list = members_form.cleaned_data['members']

            for member in members_list:
                if not chat.member_set.filter(user=member):
                    new_member = Member(chat=chat, user=member)
                    new_member.save()
        else:
            context['status'] = 'error'

        return JsonResponse(context)
    else:
        members_form = ChatMember()

    context['members_form'] = members_form

    return render(request, 'Chat/chat_member_form.html', context)


def create_conversation(request):
    context = {
        'status': 'success',
    }
    path = request.META['HTTP_REFERER']
    from_house = path.find('/house/')
    from_user = path.find('/user/')

    redirect = False
    if from_house > 0 or from_user > 0:
        redirect = True
    print(redirect)

    if request.method == 'POST':
        members_form = ChatMember(request.POST)
        if members_form.is_valid():
            print('created')
            try:
                opponent = UserExt.objects.get(username=request.POST['members'])
                user = request.user

                chat = Chat.chat_objects.has_conversation(user, opponent)

                if not chat:
                    chat_name = "%s|%s" % (user.username, opponent.username)
                    chat = Chat(name=chat_name, chat_type=Chat.P2P)
                    chat.save()

                    member1 = Member(chat=chat, user=opponent)
                    member2 = Member(chat=chat, user=user)

                    member1.save()
                    member2.save()
                    context['mini_chat'] = render_to_string('Chat/chat_mini_block.html',
                                                            {'chat': chat})
                context['slug'] = chat.slug


            except UserExt.DoesNotExist:
                context['status'] = 'user_not_exit'
        else:
            print(members_form.errors)

        if redirect:
            print(reverse('chat.page'))
            return HttpResponseRedirect(reverse('chat.page') + "#" + chat.slug)
        return JsonResponse(context)
    else:
        members_form = ChatMember()

    context['members_form'] = members_form
    context['conversation'] = True

    return render(request, 'Chat/chat_member_form.html', context)


def create_chat(request):
    context = {
        'status': 'success',
    }
    exs_chat = None
    if 'chat_slug' in request.GET:
        try:
            exs_chat = Chat.objects.get(slug=request.GET['chat_slug'])
        except Chat.DoesNotExist:
            exs_chat = None

    user = UserExt.objects.get(id=request.user.id)
    if request.method == 'POST':
        chat_form = ChatForm(request.POST, request.FILES)

        if chat_form.is_valid():
            if exs_chat:
                chat = chat_form.save(exs_chat)
            else:
                chat = chat_form.save()
                member = Member(chat=chat, user=user, status=Member.CREATOR)
                member.save()
            print(chat)
            chat.title = chat.get_chat_title(user)
            context['mini_chat'] = render_to_string('Chat/chat_mini_block.html',
                                                    {'chat': chat})
            context['slug'] = chat.slug

        return JsonResponse(context)

    else:
        if exs_chat:
            chat_form = ChatForm(initial={'name': exs_chat.name,
                                          'chat_type': exs_chat.chat_type})
        else:
            chat_form = ChatForm()

    context['chat_form'] = chat_form
    context['is_creating'] = True
    return render(request, 'Chat/chat_create_form.html', context)


def get_user(request):
    if 'q' in request.GET:

        try:
            user = UserExt.objects.filter(username=request.GET['q']).values('username', 'id')[0]
            user_data = []
            user_data.append({'name': user['username']})
            user_data.append({'id': user['id']})
            return JsonResponse({'user_data': user_data})
        except IndexError:
            return HttpResponse('none')


def load_users(request):
    if 'q' in request.GET:

        users = UserExt.objects.filter(username__istartswith=request.GET['q']).values('username')
        users_list = []
        for user in users:
            if user['username'] != request.user.username:
                users_list.append({'name': user['username']})
        return JsonResponse({'users_list': users_list})
    return HttpResponse('uncorrected request')


@login_required
def chat_list(request):

    user = UserExt.objects.get(id=request.user.id)
    chats = Chat.chat_objects.users_chats(user.id).order_by("name")
    print(open)
    chats_list = []
    for chat in chats:
        chat.user_new_message = chat.has_new_messages(user)
        chat.image = chat.get_image(user)
        chat.title = chat.get_chat_title(user)
        chats_list.append(chat)

    context = {
        'chats': chats_list,
    }
    return render(request, 'Chat/chats_page.html', context)


def chat_block(request, chat_slug):
    user = UserExt.objects.get(id=request.user.id)
    chat = get_object_or_404(Chat, slug=chat_slug)

    try:
        member = chat.member_set.get(user=user)
    except Chat.DoesNotExist:
        return Http404

    if 'since' in request.GET:
        date_since = datetime.strptime(request.GET['since'], '%d-%m-%Y %H:%M')
        messages = Message.message_object.last_10_messages(chat, date_since)

        return render(request, 'Chat/messages_list.html', {'messages': messages})

    messages = Message.objects.filter(chat=chat).order_by('-date')[0:10]
    chat_title = member.user_chat_title()
    context = {
        'chat': chat,
        'messages': messages,
        'members_form': ChatMember(),
        'chat_title': chat_title,

    }
    if chat.is_creator(user):
        context['creator'] = True
    return render(request, 'Chat/chat_block.html', context)


def create_message(request):

    user = UserExt.objects.get(id=request.user.id)

    print(request.POST)
    print(request.FILES)
    errors_file_type = []

    if request.method == 'POST':

        chat = get_object_or_404(Chat, slug=request.POST['chat_slug'])

        form_message = MessageForm(request.POST)
        form_attach = AttachmentForm(request.FILES)

        if form_message.is_valid():
            errors_file_type = (handle_uploaded_file(request.FILES))
            if not len(form_message.cleaned_data['text']) and not (len(request.FILES)):
                errors_file_type.append('empty')
            else:
                message = form_message.save(user, chat)
                save_attach(request.FILES, message, MessageAttachment)

                return JsonResponse({'message': message.id})
    else:
        form_message = MessageForm()
        form_attach = AttachmentForm()

    return render(request, 'Chat/form_message_block.html', {
        'form_message': form_message,
        'form_attach': form_attach,
        'errors_file_type': errors_file_type
    })


def chat_delete(request):
    if request.POST:
        try:
            chat = Chat.objects.get(slug=request.POST['chat_slug'])
            member = chat.member_set.filter(user=request.user)
            if member:
                member.delete()
        except Chat.DoesNotExist:
            return JsonResponse({'error': "chat isn't exist"})

    return JsonResponse({'deleted': "success"})
