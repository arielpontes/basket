import requests
from django.conf import settings
from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from basket.exceptions import BadRequestException
from basket.models import Country, Game, League, Team
from basket.serializers import GameSerializer


def refresh_db(querystring):
    """Pull data from API-BASKETBALL and store it locally"""
    url = settings.GAMES_ENDPOINT

    headers = {
        "X-RapidAPI-Key": settings.RAPID_API_KEY,
        "X-RapidAPI-Host": settings.RAPID_API_HOST,
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    errors = response.json()["errors"]
    if errors:
        raise BadRequestException(errors)
    games = response.json()["response"]
    for game_dict in games:
        league, _ = League.objects.get_or_create(
            id=game_dict["league"]["id"], defaults=game_dict["league"]
        )
        game_dict["league"] = league
        country, _ = Country.objects.get_or_create(
            id=game_dict["country"]["id"], defaults=game_dict["country"]
        )
        game_dict["country"] = country
        home_team, _ = Team.objects.get_or_create(
            id=game_dict["teams"]["home"]["id"],
            defaults=game_dict["teams"]["home"],
        )
        game_dict["home_team"] = home_team
        away_team, _ = Team.objects.get_or_create(
            id=game_dict["teams"]["away"]["id"],
            defaults=game_dict["teams"]["away"],
        )
        game_dict["away_team"] = away_team
        del game_dict["teams"]

        game_dict["home_score"] = game_dict["scores"]["home"]
        game_dict["away_score"] = game_dict["scores"]["away"]
        del game_dict["scores"]

        Game.objects.update_or_create(id=game_dict["id"], defaults=game_dict)


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "head", "patch", "delete"]

    def get_queryset(self):
        user_is_admin = self.request.user.is_staff
        refresh = bool(self.request.query_params.get("refresh"))
        options = ["date", "league", "season", "team"]
        querystring = {
            option: self.request.query_params.get(option)
            for option in options
            if self.request.query_params.get(option)
        }
        if refresh:
            if not user_is_admin:
                raise (
                    PermissionDenied(
                        "Only admin users can refresh the local DB with data "
                        "from RapidAPI."
                    )
                )
            refresh_db(querystring)
        params = {**querystring}
        if "season" in params:
            params["league__season"] = params.pop("season")
        if "date" in params:
            params["date__date"] = params.pop("date")

        qs = super().get_queryset()
        if params:
            qs = qs.filter(**params)
        if not user_is_admin:
            countries = []
            if self.request.user.profile:
                countries = self.request.user.profile.countries.all()
            qs = qs.filter(country__in=countries).filter(
                Q(user=None) | Q(user=self.request.user)
            )
        return qs

    def get_permissions(self):
        if self.action == "assign":
            # Only allow normal users to use PATCH for the "assign" action
            self.http_method_names = ["get", "head", "patch"]
            # Set the permissions for the "assign" action
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.request.method in ["PATCH", "DELETE"]:
            # Require admin status for PATCH and DELETE methods on other actions
            self.permission_classes = [permissions.IsAdminUser]
        else:
            # Set the default permissions for other actions and methods
            self.permission_classes = [permissions.IsAuthenticated]

        return super().get_permissions()

    @action(detail=False, methods=["get"])
    def assigned(self, request):
        games = self.get_queryset().filter(user=self.request.user)
        serializer = self.get_serializer(games, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def unassigned(self, request):
        games = self.get_queryset().filter(user=None)
        serializer = self.get_serializer(games, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"])
    def assign(self, request, pk=None):
        game = self.get_object()
        game.user = request.user
        game.save()
        serializer = self.get_serializer(game)
        return Response(serializer.data)
