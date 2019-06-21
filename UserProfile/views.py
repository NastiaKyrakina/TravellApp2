from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, JsonResponse, QueryDict, HttpResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from UserProfile.forms import *
from UserProfile.models import UserExt, save_attach, Diary

from datetime import datetime

from django.core.mail.message import EmailMessage

from Lib.FileFormats import handle_uploaded_file

from UserProfile.models import UserInfo

# Create your views here.


def payment_page(request):
    return render(request,
                  "UserProfile/payment/payment_page.html", {'signature': "ZZrpaLg2Lbipxu+9ZP0Irhdcg2w=",
                                                            'data': "eyJwdWJsaWNfa2V5IjoiaTg3ODE1ODI5NjQiLCJ2ZXJzaW9uIjoiMyIsImFjdGlvbiI6InBheSIsImFtb3VudCI6IjEwMCIsImN1cnJlbmN5IjoiVUFIIiwiZGVzY3JpcHRpb24iOiIiLCJvcmRlcl9pZCI6IjAwMDAwMSJ9"})


def verification_send_page(request):
    user = UserExt.objects.get(pk=request.user.pk)
    form_verification_send = VerificationSendForm()
    if user.userinfo.virifield == UserInfo.UNDF:
        if request.method == 'POST':
            form_verification_send = VerificationSendForm(request.POST)
            if form_verification_send.is_valid():
                # Создание, наполнение, отплавка сообщения
                email = EmailMessage()
                email.subject = "Verification request. User: " + user.username
                email.body = form_verification_send.data['message']
                email.from_email = user.email
                email.to = ['travelappservice@gmail.com']
                image1 = request.FILES['image1']
                image2 = request.FILES['image2']
                email.attach(image1.name, image1.read(), image1.content_type)
                email.attach(image2.name, image2.read(), image2.content_type)
                email.send()
                user.userinfo.virifield = UserInfo.WAIT
                user.userinfo.save()
                return HttpResponseRedirect('/user/verification/send')

    return render(request,
                  'UserProfile/verification/verification_send_page.html',
                  {'form_verification_send': form_verification_send}) \
        if user.userinfo.virifield == UserInfo.UNDF \
        else render(request,
                    'UserProfile/verification/verification_status_page.html',
                    {'UserStatus': UserInfo})


def create_diary(request):
    user = UserExt.objects.get(pk=request.user.pk)
    try:
        current_diary = user.diary_set.get(status=Diary.ACTIVE)
    except Diary.DoesNotExist:
        current_diary = None

    if request.method == 'POST':
        form_diary = DiaryForm(request.POST, request.FILES)

        if form_diary.is_valid():

            new_diary = form_diary.save(user)
            if current_diary:
                current_diary.status = Diary.FROZEN
                current_diary.save()
            return HttpResponseRedirect('/user/diary/%s/' % new_diary.id)


    else:
        form_diary = DiaryForm()

    return render(request,
                  'UserProfile/create_diary.html',
                  {'form_diary': form_diary,
                   'current_diary': current_diary,
                   'is_creating': True,
                   })


def user_diaries(request):
    pass


def diary_page(request, diary_id):
    diary = get_object_or_404(Diary, id=diary_id)
    markers = diary.marker_set.all()
    notes = []
    for marker in markers:
        notes.append(marker.note)
    return render(request, 'UserProfile/diary_page.html', {'diary': diary,
                                                           'notes': notes
                                                           })

def diary_markers(request, diary_id):
    if 'mrkset' in request.GET:
        diary = get_object_or_404(Diary, id=diary_id)
        markers = diary.marker_set.all()
        marker_set = []
        for marker in markers:
            marker_json = {}
            marker_json['lat'] = marker.lat
            marker_json['lng'] = marker.lng
            marker_json['text'] = marker.note.text
            marker_set.append(marker_json)
        return JsonResponse({'marker_set': marker_set})
    return HttpResponse('false')


def home(request, user_id):
    user = get_object_or_404(UserExt, pk=user_id)
    status = 'none'
    try:
        user_info = UserInfo.objects.get(pk=user.pk)
        status = user.userinfo.STATUS_TYPE[request.user.userinfo.status]
    except UserInfo.DoesNotExist:
        user_info = None


    notes = user.get_new_note_portion()
    diaries = user.diary_set.all()

    data = {
        'user': user,
        'status': status,
        'is_owner': False,
        'notes': notes,
        'diaries': diaries,
            }

    if user_id == request.user.pk:
        data['is_owner'] = True

    return render(request, "UserProfile/home.html", data)


def load_notes(request, user_id):
    user = get_object_or_404(UserExt, pk=user_id)
    if request.is_ajax():

        since = None
        if 'since' in request.GET:
            print(request.GET['since'])
            since = datetime.strptime(request.GET['since'], '%d-%m-%Y %H:%M')

        notes = user.get_new_note_portion(since)

        data = {
            'notes': notes,
        }
        page = render_to_string('UserProfile/notes_list.html', data)
        response = {'html': page}
        return JsonResponse(response)

    return Http404


@login_required
def note_page(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    is_owner = (request.user == note.user)
    data = {
        'note': note,
        'is_owner': is_owner,
    }
    return render(request, 'UserProfile/note_page.html', data)


@login_required
def note_create_page(request):
    user = UserExt.objects.get(pk=request.user.pk)
    errors_file_type = []

    try:
        current_diary = user.diary_set.get(status=Diary.ACTIVE)
    except Diary.DoesNotExist:
        current_diary = None

    if request.method == 'POST':
        form_note = NoteForm(request.POST)
        form_attach = AttachmentForm(request.POST, request.FILES)
        form_marker = MarkerForm(request.POST)

        if form_note.is_valid():
            errors_file_type = (handle_uploaded_file(request.FILES))
            if not len(form_note.cleaned_data['text']) and not (len(request.FILES)):
                errors_file_type.append(_('Empty post!'))

            if not errors_file_type:
                new_note = form_note.save(commit=False)
                new_note.user = user
                new_note.save()

                save_attach(request.FILES, new_note, Attachment)

                if current_diary:
                    new_marker = form_marker.save(commit=False)
                    new_marker.diary = user.diary_set.filter(status=Diary.ACTIVE).first()
                    new_marker.note = new_note
                    new_marker.save()

                if request.is_ajax():
                    return render(request,
                                  'UserProfile/note_block.html',
                                  {'note': new_note,
                                   'is_creating': True,
                                   })

                return HttpResponseRedirect('/user/%s/' % request.user.pk)

            else:
                print(form_note.errors)
                print(form_marker.errors)
                return JsonResponse({'errors': errors_file_type})

    else:

        form_note = NoteForm()
        form_attach = AttachmentForm()
        form_marker = MarkerForm()

    return render(request,
                  'UserProfile/includes/create_note.html',
                  {'form_note': form_note,
                   'form_attach': form_attach,
                   'form_marker': form_marker,
                   'is_creating': True,
                   'errors_type': errors_file_type,
                   'current_diary': current_diary
                   })


@login_required
def note_edit_page(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    if request.user != note.user:
        return Http404

    if request.method == 'POST':
        form_note = NoteForm(request.POST)

        if form_note.is_valid():

            note.text = form_note.cleaned_data['text']
            note.save()
            if request.is_ajax():
                return JsonResponse({'text': note.text,
                                     'status': 'success'})
            return HttpResponseRedirect('/user/%s/' % request.user.pk)
        else:
            if request.is_ajax():
                return JsonResponse({'text': note.text,
                                     'status': 'fail'})
    else:
        form_note = NoteForm(instance=note)

    data = {
        'form_note': form_note,
        'note': note,
            }

    template = 'UserProfile/create_edit_note_block.html'

    return render(request, template, data)


def delete_note(request):
    if request.method == 'POST':
        note = Note.objects.get(pk=int(QueryDict(request.body).get('notepk')))
        if request.user == note.user:
            note.deleted = datetime.now()
            note.save()
            response_data = {}
            response_data['msg'] = 'Post was deleted.'
            return JsonResponse(response_data)

    return JsonResponse({"msg": "this isn't happening"})


def about_page(request):
    return render(request, 'UserProfile/about_page.html')


def edit_diary(request, diary_id):
    diary = get_object_or_404(Diary, id=diary_id)
    user = UserExt.objects.get(pk=request.user.pk)

    if user != diary.user:
        return Http404

    if request.method == 'POST':
        form_diary = DiaryForm(request.POST, request.FILES, instance=diary)

        if form_diary.is_valid():
            diary.title = form_diary.cleaned_data['title']
            diary.about = form_diary.cleaned_data['about']
            diary.date_finish = form_diary.cleaned_data['date_finish']
            diary.photo = form_diary.cleaned_data['photo']
            diary.save()

            return HttpResponseRedirect('/user/diary/%s/' % diary.id)

    else:
        form_diary = DiaryForm(instance=diary)

    return render(request,
                  'UserProfile/create_diary.html',
                  {'form_diary': form_diary,
                   })


def delete_diary(request):
    if request.method == 'POST':
        diary = Diary.objects.get(pk=int(QueryDict(request.body).get('diarypk')))

        if request.user == diary.user:
            diary.delete()
            return JsonResponse({"locate": request.user.id})

    return JsonResponse({"msg": "this isn't happening"})


def change_diary(request):
    status = 'fail'

    if request.method == 'POST':
        diary_id = request.POST['diarypk']
        try:
            diary = Diary.objects.get(id=diary_id)
            if request.user == diary.user and not diary.is_finish():
                if diary.is_active():
                    diary.status = Diary.FROZEN
                else:
                    diary.status = Diary.ACTIVE

                status = diary.status

                diary.save()

        except Diary.DoesNotExist:
            status = 'fail'
    return JsonResponse({'status': status})
