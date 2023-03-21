# deals/tests/tests_form.py
import shutil
import tempfile

from posts.forms import PostForm
from posts.models import Post, Group
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model


# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()
# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsImgTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Ss')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        self.user = PostsImgTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_img_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст картинка',
            'image': uploaded,
            'group': self.group.id
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый текст',
            group=self.group,
            image=uploaded
        )
        post_image = Post.objects.first().image

        self.assertEqual(Post.objects.count(), posts_count + 2)
        self.assertTrue(response, reverse('posts:post_create'))
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                image='posts/small.gif'
            ).exists()
        )
        self.assertEqual(post_image, 'posts/small.gif')

    def test_group_img(self):
        # posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст картинка',
            'image': uploaded,
            'group': self.group.id
        }
        # Отправляем POST-запрос
        self.authorized_client.post(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
            data=form_data,
            follow=True
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый текст',
            group=self.group,
            image=uploaded
        )
        post_image_g = Post.objects.first().image
        self.assertEqual(post_image_g, post_image_g)

    def test_profile_img(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый текст',
            group=self.group,
            image=uploaded
        )
        self.authorized_client.get('posts: profile',
                                   kwargs={'username': self.user})
        post_image_p = Post.objects.first().image
        self.assertEqual(post_image_p, post_image_p)

    # def test_index_img(self):
    #    self.authorized_client.get(reverse('index'))
    #    post_image_i = Post.objects.first().image
    #    self.assertEqual(post_image_i, 'posts/small.gif')

    # def test_post_img(self):
