from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings


def login_view(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Password is not correct")
        except:
            messages.error(request, "User doesn't exist")

    context = {"page": page}
    return render(request, "Base/login_register.html", context)


def logoutUser(request):
    logout(request)
    return redirect("home")


def register_Page(request):
    page = "register"
    form = MyUserCreationForm()

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, f"Account has been Created: {user.username}")
            login(request, user)
            return redirect("home")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
                    print(f"{field}: {error}")
    context = {"page": page, "form": form}
    return render(request, "Base/login_register.html", context)


######
def home(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)
        | Q(host__username__icontains=q)
        | Q(name__icontains=q)
    )

    topics = Topic.objects.all()
    topics_count = topics.count()
    topics = topics[0:5]

    room_count = rooms.count()

    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages,
        "topics_count": topics_count,
    }
    return render(request, "Base/home.html", context)


######


def room(request, pk):
    message = request.POST.get("body", "").strip()
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == "POST":
        if len(message) != 0:
            message = Message.objects.create(
                user=request.user, room=room, body=request.POST.get("body")
            )
            room.participants.add(request.user)
            return redirect("room", pk=room.id)
    context = {
        "room": room,
        "room_messages": room_messages,
        "participants": participants,
    }
    return render(request, "Base/room.html", context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    if request.method == "POST":
        if user.avatar != settings.DEFAULT_IMAGE_PATH:
            user = request.user
            user.avatar.delete()
            user.avatar = settings.DEFAULT_IMAGE_PATH
            user.save()
        return redirect("profile_page", pk=request.user.id)

    context = {
        "user": user,
        "rooms": rooms,
        "room_messages": room_messages,
        "topics": topics,
    }
    return render(request, "Base/profile.html", context)


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        new_room = Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )
        new_room_id = new_room.id
        return redirect("room", pk=new_room_id)
    context = {"form": form, "topics": topics}
    return render(request, "Base/form.html", context)


@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not the owner of the room")

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")
        room.save()
        return redirect("room", pk=room.id)
    context = {"form": form, "topics": topics, "room": room}
    return render(request, "base/form.html", context)


@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not the owner of the room")

    if request.method == "POST":
        room.delete()
        return redirect("home")
    context = {"object": room}
    return render(request, "base/delete.html", context)


@login_required(login_url="login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("You are not the owner of the room")

    if request.method == "POST":
        room_id = message.room.id
        message.delete()
        return redirect("room", pk=room_id)
    context = {"object": message}
    return render(request, "base/delete.html", context)


@login_required(login_url="login")
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("profile_page", pk=user.id)

    context = {"form": form}
    return render(request, "Base/update_user.html", context)


def topicsPage(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    topics = Topic.objects.filter(name__icontains=q)
    all_topics = Topic.objects.all()
    list_all = []

    context = {"topics": topics, "all_topics": all_topics, "list_all": list_all}
    return render(request, "Base/topics.html", context)


def activityPage(request):
    room_messages = Message.objects.all()
    context = {"room_messages": room_messages}
    return render(request, "Base/activity.html", context)
