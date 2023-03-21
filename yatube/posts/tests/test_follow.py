from django.test import Client, TestCase
from posts.models import Post, User
from django.contrib.auth import get_user_model
from posts.models import Post, User, Follow


User = get_user_model()


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Ss')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост for follow',
        )

    def setUp(self):
        self.user_1 = User.objects.create_user(username='follower')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_1)
        self.another = Client()

    def test_folow(self):
        Follow.objects.all().delete()
        following = self.authorized_client.get(
            'posts:profile_follow',
            kwargs={'username': self.user.username})
        follows = Follow.objects.filter(user=self.user,
                                        author=self.user)
        self.assertTrue(following, follows)
        self.assertEqual(Follow.objects.all().count(), 0)
