from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import Post, Category, Tag, Comment
from django.contrib.auth import get_user_model
from ckeditor.fields import RichTextField
from django import forms

User = get_user_model()

# Form to update profile picture
class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture']

# Form to edit profile
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'bio']

    # Custom validation with RegexValidator for first name, last name, and username fields
    space_and_letter = RegexValidator(
        regex=r'^[a-zA-Z\s]*$',  # Space and letters only
        message="This field can only contain letters and spaces.",
        code='invalid'
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        validators=[space_and_letter],
        error_messages={
            'required': 'Please provide your first name.',
            'invalid': 'Only letters and spaces are allowed in the first name.',
        }
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        validators=[space_and_letter],
        error_messages={
            'required': 'Please provide your last name.',
            'invalid': 'Only letters and spaces are allowed in the last name.',
        }
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\S+$',  # Regex pattern for no spaces
                message="Username cannot contain spaces.",
                code='invalid_username'
            )
        ],
        error_messages={
            'required': 'Please enter a valid username.',
            'invalid': 'This username is invalid.',
        }
    )

# Form to sign up
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    # Custom validation with RegexValidator for first name, last name, and username fields
    space_and_letter = RegexValidator(
        regex=r'^[a-zA-Z\s]*$',  # Space and letters only
        message="This field can only contain letters and spaces.",
        code = 'invalid'
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        validators=[space_and_letter],
        error_messages={
            'required': 'Please provide your first name.',
            'invalid': 'Only letters and spaces are allowed in this field.',
        }
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        validators=[space_and_letter],
        error_messages={
            'required': 'Please provide your last name.',
            'invalid': 'Only letters and spaces are allowed in the last name.',
        }
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\S+$',  # Regex pattern for no spaces
                message="Username cannot contain spaces.",
                code='invalid_username'
            )
        ],
        error_messages={
            'required': 'Please enter a valid username.',
            'invalid': 'This username is invalid.',
        }
    )
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.',
            'unique': 'User with this email already exists.'
        }
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={
            'required': 'Password is required.',
        }
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={
            'required': 'Please confirm your password.',
        }
    )

# Form to create and edit a post
class PostForm(forms.ModelForm):
    # New category and tag fields
    new_category = forms.CharField(max_length=15, required=False, label='New Category')
    new_tag = forms.CharField(max_length=15, required=False, label='New Tag')

    # Custom widgets
    class Meta:
        model = Post
        fields = ['title', 'content', 'categories','tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Title'}),
            'content': RichTextField(config_name='default',),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control', 'multiple': 'multiple','placeholder': 'Categories'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control','multiple': 'multiple'}),
        }

    # Custom save method for saving the categories and tags fields
    def save(self, commit=True):
        post = super().save(commit=False)  # Create new post from the form without saving it

        # Save new categories if they are added
        new_category = self.cleaned_data.get('new_category')
        if new_category:
            category_obj, created = Category.objects.get_or_create(name=new_category)
            if created:
                post.save()
                post.categories.add(category_obj)

        # Save new tags if they are added
        new_tag = self.cleaned_data.get('new_tag')
        if new_tag:
            tag_obj, created = Tag.objects.get_or_create(name=new_tag)
            if created:
                post.save()
                post.tags.add(tag_obj)

        # Save the post and save the categories/tags (many to many fields) if commit is True
        if commit:
            post.save()
            self.save_m2m()  # Save ManyToMany relationships

        return post

# Form to comment on a post
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control','placeholder': 'Comment'}),
        }