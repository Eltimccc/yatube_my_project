# deals/tests/test_views.py
from posts.forms import PostForm
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User
from yatube.settings import POSTS_IN_PAGE

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Ss')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': self.group.slug}
                        )
            ),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username': self.user}),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': self.post.pk}
                        )
            ),
            'posts/create_post.html': (
                reverse('posts:update_post', kwargs={'post_id': self.post.pk}
                        )
            )
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PaginatorViewsTest(TestCase):
    posts_in_next_page = 3

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Ss')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        posts_in_pag = []
        for i in range(POSTS_IN_PAGE + cls.posts_in_next_page):
            posts_in_pag.append(Post(
                text=f'Тестовый пост {i}',
                author=cls.author,
                group=cls.group,
            )
            )
        Post.objects.bulk_create(posts_in_pag)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_first_page_records(self):
        test_url = {
            (reverse('index')): 'index',
            (reverse('posts:group_list',
                     kwargs={'slug': self.group.slug})): 'group_list',
            (reverse('posts:profile',
                     kwargs={'username': self.author})): 'profile'
        }
        for tested_url in test_url.keys():
            response = self.client.get(tested_url)
            self.assertEqual(
                len(response.context.get('page_obj')), POSTS_IN_PAGE)

    def test_second_page_records(self):
        test_url = {
            reverse('index') + '?page=2': 'index',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug})
            + '?page=2': 'group_list',
            reverse('posts:profile',
                    kwargs={'username': self.author})
            + '?page=2': 'profile'
        }
        for tested_url in test_url:
            response = self.client.get(tested_url)
            self.assertEqual(
                len(response.context['page_obj']),
                self.posts_in_next_page)


class PostPagesContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Ss')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
            group=cls.group,
        )

    def setUp(self):
        self.user = PostPagesContextTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.(value=value):
                form_field = response.context.get('form').fields.get(value)
                form_f = response.context.get('form')
                edit = response.context.get('is_edit')

                self.assertIsInstance(form_field, expected)
                self.assertIsInstance(form_f, PostForm)
                self.assertFalse(edit)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse
            ('posts:group_list',
             kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        self.assertEqual(task_text_0, self.post.text)

    def test_task_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context.get('post').text, self.post.text)

    def test_post_other_group(self):
        """Пост не попал в группу, для которой не был предназначен"""
        self.group_1 = Group.objects.create(
            title='Непредназначенная группа',
            slug='test-slug_1',
            description='Описание к непредназначенной группе',
        )
        self.post_1 = Post.objects.create(
            author=self.user,
            text='Непредназначенный пост',
            group=self.group_1
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))

        self.assertNotIn(self.post_1, response.context['page_obj'])
