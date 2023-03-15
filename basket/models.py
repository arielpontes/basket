from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from basket.validators import ScoreValidator, StatusValidator


class BaseExternalModel(models.Model):
    id = models.IntegerField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class League(BaseExternalModel):
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=128)
    season = models.CharField(max_length=128)
    logo = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.logo is None:
            self.logo = ""
        super().save(*args, **kwargs)


class Country(BaseExternalModel):
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=128, blank=True)
    flag = models.CharField(max_length=128, blank=True)

    class Meta:
        verbose_name_plural = "countries"

    @property
    def code_str(self):
        return self.code.strip() or "N/A" if self.code else "N/A"

    def __str__(self):
        return f"{self.name} ({self.code_str})"

    def save(self, *args, **kwargs):
        fields = ["code", "flag"]
        for field in fields:
            if getattr(self, field) is None:
                setattr(self, field, "")
        super().save(*args, **kwargs)


class Team(BaseExternalModel):
    name = models.CharField(max_length=128)
    logo = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.logo is None:
            self.logo = ""
        super().save(*args, **kwargs)


class Game(BaseExternalModel):
    date = models.DateTimeField()
    time = models.CharField(max_length=128)
    timestamp = models.CharField(max_length=128)
    timezone = models.CharField(max_length=128)
    stage = models.CharField(max_length=128, blank=True)  # ?
    week = models.CharField(max_length=128, blank=True)  # ?

    league = models.ForeignKey(
        League, on_delete=models.PROTECT, related_name="games"
    )
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, related_name="games"
    )

    status = models.JSONField(validators=[StatusValidator()])

    home_team = models.ForeignKey(
        Team, on_delete=models.PROTECT, related_name="games_where_home"
    )
    away_team = models.ForeignKey(
        Team, on_delete=models.PROTECT, related_name="games_where_away"
    )

    home_score = models.JSONField(validators=[ScoreValidator()])
    away_score = models.JSONField(validators=[ScoreValidator()])

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.home_team.name} vs. {self.away_team}"

    def clean(self):
        if self.user is not None:
            if self.user.profile is None:
                self.user.profile = Profile.objects.create(user=self.user)
            if not self.user.profile.countries.filter(
                pk=self.country.pk
            ).exists():
                raise ValidationError(
                    f"The user {self.user} is not assigned to the country {self.country}"
                )

    def save(self, *args, **kwargs):
        self.clean()
        fields = ["stage", "week"]
        for field in fields:
            if getattr(self, field) is None:
                setattr(self, field, "")
        super().save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    countries = models.ManyToManyField(Country, related_name="profiles")

    def __str__(self):
        return f"{self.user.username}'s profile"
