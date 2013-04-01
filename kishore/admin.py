from django.contrib import admin

from models import *

class SlugTitleAdmin(admin.ModelAdmin):
        prepopulated_fields = {'slug': ('title',)}

class SlugNameAdmin(admin.ModelAdmin):
        prepopulated_fields = {'slug': ('name',)}

admin.site.register(Artist, SlugNameAdmin)
admin.site.register(Image)
admin.site.register(Song, SlugTitleAdmin)
admin.site.register(Release, SlugTitleAdmin)
admin.site.register(DigitalSong, SlugNameAdmin)
admin.site.register(DigitalRelease, SlugNameAdmin)
admin.site.register(PhysicalRelease, SlugNameAdmin)
admin.site.register(Merch, SlugNameAdmin)
admin.site.register(MerchVariant)
