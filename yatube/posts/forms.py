from django.forms import ModelForm
from .models import Post, Comment, Follow


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class FollowForm(ModelForm):
    class Meta:
        model = Follow
        labels = {'user': 'подписаться:', 'author': 'user'}
        fields = ['user']
