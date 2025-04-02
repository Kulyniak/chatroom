from django.shortcuts import redirect, render
from .models import ChatRoom, Message
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.cache import never_cache


# Create your views here.
def home(request):
    chat_link = None

    if request.method == 'POST':
        password = request.POST.get('password', '')
        room = ChatRoom.objects.create(password=password if password else None)
        chat_link = request.build_absolute_uri(f'/chat/{room.id}/')

    return render(request, 'home.html', {'chat_link': chat_link})

def create_chat(request):
    room = ChatRoom.objects.create()
    return redirect(f'/chat/{room.id}')


@never_cache
def chat_room(request, chat_id):
    try:
        room = ChatRoom.objects.get(id=chat_id, is_active=True)
    except ChatRoom.DoesNotExist:
        return render(request, 'chat_expired.html')

    if room.password:
        session_key = f'chat_pass_{chat_id}'
        entered_pass = request.session.get(session_key)

        if request.method == 'POST' and 'password' in request.POST:
            if request.POST['password'] == room.password:
                request.session[session_key] = room.password
            else:
                return render(request, 'chat_password.html', {
                    'chat_id': chat_id,
                    'error': 'Incorrect password'
                })

        elif entered_pass != room.password:
            return render(request, 'chat_password.html', {'chat_id': chat_id})
    
    if timezone.now() - room.last_activity > timedelta(minutes=60):
        Message.objects.filter(chat_id=chat_id).delete()
        ChatRoom.objects.filter(id=chat_id).delete()
        room.save()
        return render(request, 'chat_expired.html')

    username = request.session.get(f'username_{chat_id}', None)

    if request.method == 'POST':
        if 'username' in request.POST and 'message' not in request.POST:
            request.session[f'username_{chat_id}'] = request.POST['username']
            username = request.POST['username']
        elif 'message' in request.POST:
            message_text = request.POST['message']
            Message.objects.create(chat=room, username=username, text=message_text)
            room.last_activity = timezone.now()
            room.save()


    messages = Message.objects.filter(chat=room).order_by('timestamp')


    expires_at = room.last_activity + timedelta(hours=1)
    minutes_left = int((expires_at - timezone.now()).total_seconds() // 60)
    if minutes_left < 0:
        minutes_left = 0

    return render(request, 'chatroom.html', {
        'chat_id': chat_id,
        'username': username,
        'messages': messages,
        'minutes_left': minutes_left,
        'expires_at': expires_at
    })
    


def check_chat_status(request, chat_id):
    try:
        room = ChatRoom.objects.get(id=chat_id)
        return JsonResponse({'active': room.is_active})
    except ChatRoom.DoesNotExist:
        return JsonResponse({'active': False})

    
def delete_chat(request, chat_id):
    if request.method == 'POST':
        Message.objects.filter(chat_id=chat_id).delete()
        ChatRoom.objects.filter(id=chat_id).delete()
    
    return redirect('home')
            