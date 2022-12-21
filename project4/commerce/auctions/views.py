from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comment, Bid


def index(request):
    allListings = Listing.objects.filter(isActive=True)
    categories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": allListings, "categories": categories
    })

def displayCategory(request):
    if request.method == "POST":
        categoryform = request.POST["category"]
        category = Category.objects.get(categoryName=categoryform)
        allListings = Listing.objects.filter(isActive=True, category=category)
        categories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": allListings, "categories": categories, "message": "No pokemons from this category"
        })

def listing(request, id):
    listingData = Listing.objects.get(pk=id)
    isListinginWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    return render(request, "auctions/listing.html", {
        "listing": listingData, "isListinginWatchlist": isListinginWatchlist, "comments": allComments
    })


def removeWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    current_user = request.user
    listingData.watchlist.remove(current_user)
    return HttpResponseRedirect(reverse('listing', args=(id, )))


def addtoWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    current_user = request.user
    listingData.watchlist.add(current_user)
    return HttpResponseRedirect(reverse('listing', args=(id, )))

def displayWatchlist(request):
    current_user = request.user
    listings = current_user.listingWatchlist.all()
    return render(request, "auctions/displayWatchlist.html", {
        "listings": listings
    })
   
def addComment(request, id):
    currentUser = request.user
    listingData = Listing.objects.get(pk=id)
    message = request.POST["newComment"]
    
    new_comment = Comment(author=currentUser, listing=listingData, message=message)
    new_comment.save()
    isListinginWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    return render(request, "auctions/listing.html", {
        "listing": listingData, "isListinginWatchlist": isListinginWatchlist, "comments": allComments
    })

def addBid(request, id):
    new_bid = request.POST["newBid"]
    listingData = Listing.objects.get(pk=id)
    isListinginWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    currentUser = request.user
    if int(new_bid) > int(listingData.price.bid):
        
        updateBid = Bid(bid=int(new_bid), user=currentUser)
        updateBid.save()
        listingData.price.bid = int(new_bid)
        listingData.save()
        return render(request, "auctions/listing.html", {
            "listing": listingData, "message": "Bid updated successfully", "update": True, "isListinginWatchlist": isListinginWatchlist, "comments": allComments
        })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listingData, "message": "Invalid Bid", "update": False, "isListinginWatchlist": isListinginWatchlist, "comments": allComments
        })





def createListing(request):
    if request.method == "GET":
        categories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": categories
        })
    else:
        title = request.POST["title"]
        description = request.POST["description"]
        price = request.POST["price"]
        category = request.POST["category"]
        imageurl = request.POST["imageurl"]
        currentUser = request.user
        category_data = Category.objects.get(categoryName=category)
        bid = Bid(bid=int(price), user=currentUser)
        bid.save()
        newListing = Listing(title=title, description=description, imageUrl=imageurl, price=bid, owner=currentUser, category=category_data)
        newListing.save()
        return HttpResponseRedirect(reverse("index"))


   
        


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
