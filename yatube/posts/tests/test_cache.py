from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, User

User = get_user_model()


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='Ss'),
            text='Тестовый кеш')

    def setUp(self):
        self.guest_client = Client()
        self.user = self.post.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index(self):
        """Тест кэш index"""
        get_index = self.authorized_client.get(reverse('index'))
        post4cache = Post.objects.get(pk=1)
        post4cache.text = 'Кеш текст'
        post4cache.save()
        test1 = self.authorized_client.get(reverse('index'))
        self.assertEqual(get_index.content, test1.content)
        cache.clear()
        test2 = self.authorized_client.get(reverse('index'))
        self.assertNotEqual(get_index.content, test2.content)
