from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(UserEmail)
admin.site.register(EmailOTP)
admin.site.register(Follow)
admin.site.register(Notification)