import json

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.forms.models import ModelForm

from basket.models import Country, Game, League, Profile, Team

User = get_user_model()


class CountryAdmin(admin.ModelAdmin):
    pass


class GameAdmin(admin.ModelAdmin):
    list_display = ("game", "date", "league", "country")

    @admin.display(description="Game")
    def game(self, obj):
        return str(obj)


class LeagueAdmin(admin.ModelAdmin):
    pass


class TeamAdmin(admin.ModelAdmin):
    pass


class AlwaysChangedModelForm(ModelForm):
    def has_changed(self):
        return True


class ProfileInline(admin.StackedInline):
    model = Profile
    form = AlwaysChangedModelForm
    verbose_name_plural = "profile"
    extra = 0


def custom_data(self):
    return json.dumps(
        {
            "name": "#profile",
            "options": {
                "prefix": "profile",
                "addText": "Create user profile",
                "deleteText": "Remove",
            },
        }
    )


class UserAdmin(BaseUserAdmin):
    def change_view(self, *args, **kwargs):
        self.inlines = (ProfileInline,)
        return super().change_view(*args, **kwargs)

    def add_view(self, *args, **kwargs):
        self.inlines = []
        return super().add_view(*args, **kwargs)

    def get_inline_formsets(
        self, request, formsets, inline_instances, obj=None
    ):
        inline_formsets = super().get_inline_formsets(
            request, formsets, inline_instances, obj=obj
        )
        if inline_formsets:
            formset = inline_formsets[0]
            formset.inline_formset_data = custom_data.__get__(formset)
        return inline_formsets


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(League, LeagueAdmin)
admin.site.register(Team, TeamAdmin)
