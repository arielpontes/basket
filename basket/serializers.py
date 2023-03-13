from rest_framework import serializers
from basket.models import Game


class GameSerializer(serializers.ModelSerializer):
    status = serializers.JSONField()
    teams = serializers.JSONField()
    scores = serializers.JSONField()

    class Meta:
        model = Game
        fields = "__all__"
