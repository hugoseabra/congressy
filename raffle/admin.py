from django.contrib import admin

from raffle.models import Winner, Raffle


admin.site.register(Raffle)
admin.site.register(Winner)
