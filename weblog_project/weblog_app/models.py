from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField

# Create your models here.

# Category model
class Category(models.Model):
    # Create name field in Category model in db
    name = models.CharField(max_length=15)

    # Every category will be one user owner, it will be unique and other users can use them as well.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_DEFAULT, default=14)

    def __str__(self):
        return self.name

# Tag model
class Tag(models.Model):
    # Create name field in Tag model in db
    name = models.CharField(max_length=15)

    # Every tag will be one user owner, it will be unique and other users can use them as well.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_DEFAULT, default=14)

    def __str__(self):
        return self.name

# Post model
class Post(models.Model):
    # Create title field in Post model in db
    title = models.CharField(max_length=48, null=False, blank=False)

    # (Relate author with User model with ForeignKey. Post have only one author, but
    # User can have multiple posts.)
    # (Delete the post if the user is deleted with "on_delete=models.CASCADE")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False,blank=False)

    # Create content field in Post model in db with RichTextField (CKEditor)
    content = RichTextField(null=False, blank=False)

    # Save post creation date with auto_now_add
    created_at = models.DateTimeField(auto_now_add=True)

    # Save post update date with auto_now
    updated_at = models.DateTimeField(auto_now=True)

    # (Relate post with Category model with ManyToManyField. Post can have multiple categories,
    # and Category can have multiple posts.)
    categories = models.ManyToManyField(Category, related_name="posts",blank=False)
    tags = models.ManyToManyField(Tag, related_name="posts", blank=False)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='post_likes', blank=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title

# Comment model
class Comment(models.Model):
    # Every comment belongs to one post and one user. The comment will be deleted
    # when the post or the user is deleted.
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Create content, tags, likes, created_at, updated_at fields in Comment model in db
    content = models.TextField(max_length=200, blank=False, null=False)
    tags = models.ManyToManyField(Tag, related_name="comments", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='comment_likes', blank=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"Comment by {self.user} on {self.post.title}"

# Function for creating file name special to user
def make_user_special(instance, filename):
    parts = filename.split('.')
    ext = parts[-1]
    name = "".join(parts[:-1])
    filename = f'user_{instance.id}_{slugify(name)}.{ext}'
    return f'profile_pics/{filename}'

# User model
class CustomUser(AbstractUser):
    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False
    )

    last_name = models.CharField(
        max_length=150,
        blank=False,
        null=False
    )

    email = models.EmailField(
        unique=True,
        max_length=254,
        blank=False,
        null=False
    )

    # Add bio field, allowing null (for db) and blank (for inputs)
    bio = models.CharField(max_length=50, blank=True, null=True, default="Hello, I'm new user!")

    # Add profile picture field
    profile_picture = models.ImageField(upload_to=make_user_special, default="profile_pics/default.png")

    # Add "last active" field
    last_active = models.DateTimeField(null=True, blank=True)

    # Separate groups and permissions to prevent collisions
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',
        blank=True,
        help_text='The groups this user belongs to.',  # Add help text to the admin panel
        verbose_name='groups'  # Define the name in the admin panel
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username


