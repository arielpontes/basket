from djongo import models


class Status(models.Model):
    long = models.CharField(max_length=128)
    short = models.CharField(max_length=128)
    timer = models.CharField(max_length=128)  # ?

    class Meta:
        abstract = True


class League(models.Model):
    id = models.ObjectIdField()
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=128)
    season = models.CharField(max_length=128)
    logo = models.CharField(max_length=128)


class Country(models.Model):
    id = models.ObjectIdField()
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=128)
    flag = models.CharField(max_length=128)


class Team(models.Model):
    id = models.ObjectIdField()
    name = models.CharField(max_length=128)
    logo = models.CharField(max_length=128)


class Teams(models.Model):
    home = models.EmbeddedField(model_container=Team)
    away = models.EmbeddedField(model_container=Team)

    class Meta:
        abstract = True


class Score(models.Model):
    quarter_1 = models.PositiveSmallIntegerField()
    quarter_2 = models.PositiveSmallIntegerField()
    quarter_3 = models.PositiveSmallIntegerField()
    quarter_4 = models.PositiveSmallIntegerField()
    over_time = models.PositiveSmallIntegerField()
    total = models.PositiveSmallIntegerField()

    class Meta:
        abstract = True


class Scores(models.Model):
    home = models.EmbeddedField(model_container=Score)
    away = models.EmbeddedField(model_container=Score)

    class Meta:
        abstract = True


class Game(models.Model):
    id = models.ObjectIdField()
    date = models.DateTimeField()
    time = models.CharField(max_length=128)
    timestamp = models.CharField(max_length=128)
    timezone = models.CharField(max_length=128)
    stage = models.CharField(max_length=128)  # ?
    week = models.CharField(max_length=128)  # ?

    league = models.EmbeddedField(model_container=League)
    country = models.EmbeddedField(model_container=Country)

    # Not working because of: https://github.com/doableware/djongo/issues/556
    # status = models.EmbeddedField(model_container=Status)
    # teams = models.EmbeddedField(model_container=Teams)
    # scores = models.EmbeddedField(model_container=Scores)

    status = models.JSONField()
    teams = models.JSONField()
    scores = models.JSONField()

    objects = models.DjongoManager()
