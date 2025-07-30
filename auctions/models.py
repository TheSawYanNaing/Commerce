from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Auctions(models.Model):
    title = models.CharField(max_length=64)
    price = models.IntegerField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=64, null=True, blank=True)
    active = models.BooleanField(default=True)

# Model for auction owner
class AuctionOwners(models.Model):
    auction = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="owner")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    
# Model for bidding auction
class Bids(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    auction = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="bids")
    bidPrice = models.FloatField()
    
# Comment for auctions
class Comments(models.Model):
    auction = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="comments")
    writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    description = models.TextField()
    
# For WatchList
class WatchList(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchLists")
    auction = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="watchlist")

class Winner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wins")
    auction = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="winner")