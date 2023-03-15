from rest_framework import serializers

from basket.models import Country, Game, League, Team


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        exclude = ("created_at", "updated_at")


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        exclude = ("created_at", "updated_at")


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        exclude = ("created_at", "updated_at")


class GameSerializer(serializers.ModelSerializer):
    country = CountrySerializer()
    league = LeagueSerializer()
    teams = serializers.SerializerMethodField()
    scores = serializers.SerializerMethodField()

    class Meta:
        model = Game
        exclude = (
            "created_at",
            "updated_at",
            "home_team",
            "away_team",
            "home_score",
            "away_score",
        )

    def get_teams(self, obj):
        return {
            "home": TeamSerializer(obj.home_team).data,
            "away": TeamSerializer(obj.away_team).data,
        }

    def get_scores(self, obj):
        return {
            "home": obj.home_score,
            "away": obj.away_score,
        }
