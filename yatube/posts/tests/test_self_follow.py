from django.test import Client, TestCase
from posts.models import Post, User
from django.contrib.auth import get_user_model
from posts.models import Post, User, Follow


User = get_user_model()


class FollowSelfTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Ss')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост for follow',
        )
        cls.author = cls.user

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_folow(self):
        followers = Follow.objects.all()
        follower_self = Follow.objects.create(
            user=self.user, author=self.author)
        self.assertNotEqual(follower_self, followers)
