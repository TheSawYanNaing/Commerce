from django.contrib.auth import authenticate, login, logout, decorators
from django.db import IntegrityError, models
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import Auctions, AuctionOwners, WatchList, Bids, Comments, AuctionOwners, Winner

from .models import User

# forms for auction listing
class Listing(forms.Form):
    title = forms.CharField(max_length=64, label="Title",required=True, widget=forms.TextInput(attrs={
        "class" : "form-control my-2"
    }))
    category = forms.CharField(max_length=64, label="Category(Optional)", required=False, widget=forms.TextInput(attrs={
        "class" : "form-control my-2"
    }))
    price = forms.FloatField(label="Staring Price", required=True, widget=forms.TextInput(attrs={
        "class" : "form-control my-2"
    }))
    description = forms.CharField(label="Description",required=True, widget=forms.Textarea(attrs={
        "rows" : 5,
        "class" : "form-control my-2"
    }))
    image = forms.ImageField(label="Image(Optional)", required=False, widget=forms.ClearableFileInput(attrs={
        "class" : "form-control my-2"
    }))

def index(request):
    return render(request, "auctions/index.html", {
        "listings" : Auctions.objects.filter(active=True)
    })


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

# For Creating a new listing
@decorators.login_required
def create(request):
    if request.method == "GET":
        return render(request, "auctions/create.html", {
            "form" : Listing()
        })
    
    # For post method
    # Get form 
    form = Listing(request.POST, request.FILES)
    
    if (form.is_valid()):
        title = form.cleaned_data["title"]
        price = float(form.cleaned_data["price"])
        description = form.cleaned_data["description"]
        category = form.cleaned_data["category"]
        image = form.cleaned_data["image"]
        
        auction = Auctions(title=title, price=price, category=category, description=description, image=image)
        auction.save()
        
        auctionOwner = AuctionOwners(owner=request.user, auction=auction)
        auctionOwner.save()
        
        return HttpResponseRedirect(reverse("index"))
    
    return render(request, "auctions/create.html", {
        "form" : Listing(request.POST)
    })
    

def listing(request, id):
    auction = Auctions.objects.get(pk=id)
    maxBid = auction.bids.aggregate(models.Max("bidPrice"))["bidPrice__max"]
    comments = auction.comments.all()
    winner = Winner.objects.filter(auction=auction).first()
    
    if (request.user.is_authenticated):
        return render(request, "auctions/listing.html", {
            "auction" : auction,
            "maxBid" : maxBid,
            "onWatch" : WatchList.objects.filter(owner=request.user, auction=auction).first(),
            "comments" : comments,
            "isOwner" : AuctionOwners.objects.get(auction=auction).owner == request.user,
            "winner" : winner
        })
        
    return render(request, "auctions/listing.html", {
            "auction" : auction,
            "maxBid" : maxBid,
            "comments" : comments
        })

# for bidding an auction
@decorators.login_required
def bid(request, id):
    
    # Get the auction of id 
    auction = Auctions.objects.get(pk=id)
    
    # Get the maximum bid
    maxBid = auction.bids.aggregate(models.Max("bidPrice"))["bidPrice__max"]
    
    if not maxBid:
        maxBid = 0
    
    # Getting user bid
    userBid = float(request.POST.get("bid"))
    
    if (userBid > maxBid and userBid > auction.price):
        bids = Bids(bidder=request.user, auction=auction, bidPrice = userBid)
        bids.save()
        return HttpResponseRedirect(reverse("listing", args=[id]))
    
    return render(request, "auctions/listing.html", {
            "auction" : auction,
            "maxBid" : maxBid,
            "onWatch" : WatchList.objects.filter(owner=request.user, auction=auction).first(),
            "comments" : auction.comments.all(),
            "bidError" : "Your Bid must be higher than the maximum bid"
        })
    
# for commenting
@decorators.login_required
def comment(request, id):
    auction = Auctions.objects.get(pk = id)
    
    userComment = request.POST.get("comment")
    
    comments = Comments(writer=request.user, description=userComment, auction=auction)
    
    comments.save()
    
    return HttpResponseRedirect(reverse("listing", args=[id]))
    

# for adding to watchlist
@decorators.login_required
def addWatchlist(request, id):
    auction = Auctions.objects.get(pk = id)
    
    watchlists = WatchList(owner=request.user, auction=auction)
    watchlists.save()
    
    return HttpResponseRedirect(reverse("listing", args=[id]))

@decorators.login_required
def removeWatchlist(request, id):
    auction = Auctions.objects.get(pk = id)
    
    watchlists = WatchList.objects.get(owner=request.user, auction=auction)
    
    watchlists.delete()
    
    return HttpResponseRedirect(reverse("listing", args=[id]))

# For Closing an aunction
@decorators.login_required
def close(request, id):
    # Get the aunction of id
    auction = Auctions.objects.get(pk=id)
    auction.active = False 
    auction.save()
    
    # Get the winner of auction
    maxBid = auction.bids.aggregate(models.Max("bidPrice"))["bidPrice__max"]
    
    if maxBid:
        # Get the bidder of the max bid
        bidder = Bids.objects.get(bidPrice=maxBid)
        
        # Create a row for winner
        winner = Winner(user=bidder.bidder, auction=auction)
        winner.save()
    
    return HttpResponseRedirect(reverse("listing", args=[id]))

# For watchlist
@decorators.login_required
def watchlist(request):
    # Get the watchlist of user
    userWatchLists = request.user.watchLists.all()
    
    return render(request, "auctions/watchlist.html", {
        "watchlists" : userWatchLists
    })

def category(request):
    categories = Auctions.objects.filter(active=True).values_list('category', flat=True).distinct()
    
    return render(request, "auctions/category.html", {
        "categories" : categories
    })

def topic(request, category):
    
    # Get the listing of category (category)
    auctions = Auctions.objects.filter(category=category, active=True)
    
    return render(request, "auctions/index.html", {
        "listings" : auctions
    })