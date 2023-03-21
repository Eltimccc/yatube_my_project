from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus
from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Ss')
        cls.group = Group.objects.create(
            title=('Тестовая группа'),
            slug='test_slug',
            description='Тестовое описание'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post(self):
        count_posts = Post.objects.count()
        form_data = {
            'text': 'ТеКстт',
            'group': PostCreateFormTests.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(id=PostCreateFormTests.group.id)
        author = self.user
        group = Group.objects.get(title='Тестовая группа')
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username}))
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group.id
            ).exists()
        )
        self.assertEqual(post.text, 'ТеКстт')
        self.assertEqual(author.username, 'Ss')
        self.assertEqual(group.title, 'Тестовая группа')

    def test_guest_new_post(self):
        form_data = {
            'text': 'Пост?',
            'group': PostCreateFormTests.group.id
        }
        tasks_count = Post.objects.count()
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), tasks_count)

    def test_authorized_edit_post(self):
        form_data = {
            'text': 'ТеКстт',
            'group': self.group.id
        }
        self.post = Post.objects.create(
            author=self.user,
            text=form_data['text'],
            group=self.group,
        )
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.id
        }
        response_edit = self.authorized_client.post(
            reverse('posts:update_post',
                    kwargs={
                        'post_id': self.post.id
                    }),
            data=form_data,
            follow=True,
        )

        self.post.refresh_from_db()
        self.assertEqual(response_edit.status_code, HTTPStatus.OK)
