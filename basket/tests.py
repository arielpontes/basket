from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from basket.models import Country, Game, Profile

User = get_user_model()


class TestGames(APITestCase):
    fixtures = ["test_data.json"]

    def setUp(self):
        pass

    def authenticate(self, user):
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.key}")

    def test_unauthorized(self):
        url = reverse("game-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_sees_all_games(self):
        user = User.objects.create(username="admin", is_staff=True)
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.key}")
        url = reverse("game-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), Game.objects.count())

    def test_normal_user_sees_only_their_country(self):
        user = User.objects.create(username="normal", is_staff=False)

        # Assign Romania to the user
        profile = Profile.objects.create(user=user)
        romania = Country.objects.get(code="RO")
        profile.countries.add(romania)

        # Assign specific Romania game to the user
        game = romania.games.first()
        game.user = user
        game.save()

        # Authenticate
        self.authenticate(user)

        # Fetch games for user
        url = reverse("game-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # All Romania games (assigned and unassigned) are returned
        self.assertEqual(
            len(response.json()), Game.objects.filter(country=romania).count()
        )

    def test_normal_user_does_not_see_games_assigned_to_others(self):
        user = User.objects.create(username="normal", is_staff=False)
        user2 = User.objects.create(username="normal2", is_staff=False)

        # Assign Romania to both users
        profile = Profile.objects.create(user=user)
        profile2 = Profile.objects.create(user=user2)
        romania = Country.objects.get(code="RO")
        profile.countries.add(romania)
        profile2.countries.add(romania)

        # Assign specific Romania game to user2
        game = romania.games.first()
        game.user = user2
        game.save()

        # Authenticate
        self.authenticate(user)

        # Fetch games for user
        url = reverse("game-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # The game assigned to user2 is not in the results
        self.assertEqual(
            len(response.json()),
            Game.objects.filter(country=romania).count() - 1,
        )

    def test_assigned(self):
        user = User.objects.create(username="normal", is_staff=False)

        # Assign Romania to the user
        profile = Profile.objects.create(user=user)
        romania = Country.objects.get(code="RO")
        profile.countries.add(romania)

        # Assign specific Romania game to user
        game = romania.games.first()
        game.user = user
        game.save()

        # Authenticate
        self.authenticate(user)

        # Fetch assigned games for user
        url = reverse("game-assigned")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Only the specifically assigned game is returned
        self.assertEqual(len(response.json()), 1)

    def test_unassigned(self):
        user = User.objects.create(username="normal", is_staff=False)

        # Assign Romania to the user
        profile = Profile.objects.create(user=user)
        romania = Country.objects.get(code="RO")
        profile.countries.add(romania)

        # Assign specific Romania game to user
        game = romania.games.first()
        game.user = user
        game.save()

        # Authenticate
        self.authenticate(user)

        # Fetch assigned games for user
        url = reverse("game-unassigned")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Only the unassigned games are returned
        self.assertEqual(
            len(response.json()),
            Game.objects.filter(country=romania).count() - 1,
        )

    def test_assign_assignable(self):
        user = User.objects.create(username="normal", is_staff=False)

        # Assign Romania to the user
        profile = Profile.objects.create(user=user)
        romania = Country.objects.get(code="RO")
        profile.countries.add(romania)

        # Get a random Romania game
        game = romania.games.first()

        # Authenticate
        self.authenticate(user)

        # Assign game to user
        url = reverse("game-assign", kwargs={"pk": game.pk})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Game is now assigned to user
        game.refresh_from_db()
        self.assertEqual(game.user, user)

    def test_assign_unassignable(self):
        user = User.objects.create(username="normal", is_staff=False)

        # Assign Romania to the user
        profile = Profile.objects.create(user=user)
        romania = Country.objects.get(code="RO")
        profile.countries.add(romania)

        # Get a random game from another country
        spain = Country.objects.get(code="ES")
        game = spain.games.first()

        # Authenticate
        self.authenticate(user)

        # Assign game to user
        url = reverse("game-assign", kwargs={"pk": game.pk})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Game is not assigned to user
        game.refresh_from_db()
        self.assertNotEqual(game.user, user)
