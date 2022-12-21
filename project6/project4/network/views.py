from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.http import JsonResponse

from .models import User, Post, Follow, Like


def add_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objetcs.get(pk=request.user.id)
    new_like = Like(user=user, post=post)
    new_like.save()
    return JsonResponse({"message": "liked added"})

def remove_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objetcs.get(pk=request.user.id)
    like = Like.objects.filter(user=user, post=post)
    like.delete()
    return JsonResponse({"message": "removed like"})

def index(request):
    all_posts = Post.objects.all().order_by("id").reverse()
    #pagination
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)
    all_likes = Like.objects.all()
    who_you_liked = []
    try:
        for like in all_likes:
            if like.user.id == request.user.id:
                who_you_liked.append(like.post.id)
    except:
        who_you_liked = []

    return render(request, "network/index.html", {
        "all_posts": all_posts,
        "posts_of_the_page": posts_of_the_page,
        "who_you_liked": who_you_liked
    })

#FUNCTION FOR NEW POST
def new_post(request):
    if request.method == "POST":
        content = request.POST["content"]
        user = User.objects.get(pk=request.user.id)
        post = Post(content=content, user=user)
        if post != "":
            post.save()
            return HttpResponseRedirect(reverse(index))
        return HttpResponseRedirect(reverse(index))

#EDIT FUNCTION

def edit(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)  
        edit_post = Post.objects.get(pk=post_id)
        edit_post.content = data["content"]
        edit_post.save()
        return JsonResponse({"message": "Change successful", "data": data["content"]})


#PROFILE FUNCTION
def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    all_posts = Post.objects.filter(user=user).order_by("id").reverse()
    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(user_follower=user)
    is_following = True
    try:
        check_follow = followers.filter(user=User.objects.get(pk=request.user.id))
        if len(check_follow) != 0:
            is_following = True
        else:
            is_following = False

    except:
        is_following = False
    
        #pagination
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)
    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(user_follower=user)

    return render(request, "network/profile.html", {
        "all_posts": all_posts,
        "posts_of_the_page": posts_of_the_page,
        "username": user.username,
        "following": following,
        "followers": followers,
        "is_following": is_following,
        "user_profile": user
    })

def following(request):
    current_user = User.objects.get(pk=request.user.id)
    following_people = Follow.objects.filter(user=current_user)
    all_posts = Post.objects.all().order_by('id').reverse()
    following_posts = []

    for post in all_posts:
        for person in following_people:
            if person.user_follower == post.user:
                following_posts.append(post) 
    
    paginator = Paginator(following_posts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts_of_the_page": posts_of_the_page,
    })

def follow(request):
    userfollow = request.POST["userfollow"]
    current_user = User.objects.get(pk=request.user.id)
    userfollow_data = User.objects.get(username=userfollow)
    f = Follow(user=current_user, user_follower=userfollow_data)
    f.save()
    user_id = userfollow_data.id
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))

def unfollow(request):
    userfollow = request.POST["userfollow"]
    current_user = User.objects.get(pk=request.user.id)
    userfollow_data = User.objects.get(username=userfollow)
    f = Follow.objects.get(user=current_user, user_follower=userfollow_data)
    f.delete()
    user_id = userfollow_data.id
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
