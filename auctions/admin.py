from django.contrib import admin
from .models import User, AuctionOwners, Auctions, Bids, Comments, WatchList

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email")

class AuctionOwnerAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "auction")

class AuctionsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "image", "description", "category")

class BidsAdmin(admin.ModelAdmin):
    list_display = ("id", "bidder", "auction", "bidPrice")

class CommentsAdmin(admin.ModelAdmin):
    list_display = ("id", "auction", "writer", "description")
    
class WatchListAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "auction")
# Registering
admin.site.register(User, UserAdmin)
admin.site.register(Auctions, AuctionsAdmin)
admin.site.register(AuctionOwners, AuctionOwnerAdmin)
admin.site.register(Bids, BidsAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(WatchList, WatchListAdmin)