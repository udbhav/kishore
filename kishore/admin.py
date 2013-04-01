from django.contrib import admin

from models import *

class SlugAdmin(admin.ModelAdmin):
        prepopulated_fields = {'slug': ('title',)}

class ArtistAdmin(admin.ModelAdmin):
        prepopulated_fields = {'slug': ('name',)}

admin.site.register(Artist, ArtistAdmin)
admin.site.register(Image)
admin.site.register(Song, SlugAdmin)
admin.site.register(Release, SlugAdmin)
admin.site.register(DigitalSong)
admin.site.register(DigitalRelease)
admin.site.register(PhysicalRelease)
admin.site.register(Merch)
admin.site.register(MerchVariant)
