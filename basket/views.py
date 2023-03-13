import requests
from django.conf import settings

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from basket.models import League, Country, Game
from basket.serializers import GameSerializer


def refresh_db(querystring):
    url = settings.GAMES_ENDPOINT

    headers = {
        "X-RapidAPI-Key": settings.RAPID_API_KEY,
        "X-RapidAPI-Host": settings.RAPID_API_HOST,
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    games = response.json()["response"]
    # Game.objects.bulk_create([Game(**game) for game in games])
    # import ipdb

    # ipdb.set_trace()
    for game_dict in games:
        league = League.objects.update_or_create(
            id=game_dict["league"]["id"], defaults=game_dict["league"]
        )
        game_dict["league"] = league
        country = Country.objects.update_or_create(
            id=game_dict["country"]["id"], defaults=game_dict["country"]
        )
        game_dict["country"] = country
        Game.objects.update_or_create(id=game_dict["id"], defaults=game_dict)


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        refresh = bool(self.request.query_params.get("refresh"))
        options = ["date", "league", "season", "team"]
        querystring = {
            option: self.request.query_params.get(option)
            for option in options
            if self.request.query_params.get(option)
        }
        if refresh:
            refresh_db(querystring)
        params = {**querystring}
        if "season" in params:
            params["league__season"] = params.pop("season")

        qs = super().get_queryset()
        if params:
            qs = qs.filter(**params)
        return qs
