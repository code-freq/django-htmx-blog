from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.messages.context_processors import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from . import models
from . import forms
import re
import os

# Create your views here.

# Index Page
def index(request):
    return render(request, 'index.html')

# Welcome Message
def welcome_message(request):
    return render(request, 'partials/welcome.html')

# Sign up/in buttons
def sign_buttons(request):
    return render(request, 'partials/sign_buttons.html')

# Login Required
def login_required_page(request):
    return render(request, 'login_required.html')

# Sign Up Form (from both navbar register and index page register)
def sign_up(request):
    # Check source value and set target parameter as boolean accordingly
    source = request.GET.get('source', '')
    target_base = False
    if source == 'navbar':
        target_base = True
    return render(request, 'partials/sign_up.html', {'target_base': target_base})

# Sign In Form (from both navbar login and index page login)
def sign_in(request):
    # Check source value and set target parameter as boolean accordingly
    source = request.GET.get('source', '')
    target_base = False
    if source == 'navbar':
        target_base = True
    return render(request, 'partials/sign_in.html', {'target_base': target_base})

# Process Sign Up Post Request
def sign_up_form(request):
    # Get and check source value
    source = request.POST.get('source', '')
    target_base = False
    if source == 'navbar':
        target_base = True
    form = forms.CustomUserCreationForm(request.POST or None)
    if request.method == 'POST':
        # Login and HTMX redirect to welcome page if form is valid
        if form.is_valid():
            User = form.save()
            login(request, User)
            return HttpResponse(headers={'HX-Redirect': '/welcome/'})
        else:
            # Show error with the current form if form is invalid
            return render(request, 'partials/sign_up.html', {'form': form, 'target_base': target_base})
    else:
        # Render empty form if request is GET
        return render(request, 'partials/sign_up.html',
                      {'form': forms.CustomUserCreationForm(), 'target_base': target_base})

# Process Sign In Post Request
def sign_in_form(request):
    # Get login inputs
    username = request.POST.get('username')
    password = request.POST.get('password')
    remember = request.POST.get('remember_me')

    User = get_user_model()  # Get custom user model
    # Check if user exists
    if User.objects.filter(username=username).exists():
        User = User.objects.get(username=username)
        # Check if password is correct
        if User.check_password(password):
            login(request, User)  # Login

            # Set expiration according to 'remember me'
            if remember == 'on':
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)  # On browser close

            # HTMX Redirect to home page with the message
            messages.info(request, f"Welcome back, {User.first_name} ❤")
            return HttpResponse(
                headers={'HX-Redirect': '/home/'}
            )
        # Show error if password is incorrect
        else:
            return HttpResponse("<p class='error'>Invalid password..</p>")
    # Show error if username does not exist
    else:
        return HttpResponse("<p class='error'>Username does not exist...</p>")

# Welcome Page
@login_required(login_url='/login/')
def welcome(request):
    return render(request, 'welcome_page.html')

# Home Page
@login_required(login_url='/login/')
def home(request):
    # Get most liked, commented, used categories and tags
    most_liked_posts = models.Post.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:4]
    most_commented_posts = models.Post.objects.annotate(comment_count=Count('comments')).order_by('-comment_count')[:4]
    most_used_categories = models.Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:4]
    most_used_tags = models.Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:4]

    return render(request, 'home.html', {
        'most_liked_posts': most_liked_posts,
        'most_commented_posts': most_commented_posts,
        'most_used_categories': most_used_categories,
        'most_used_tags': most_used_tags
    })

# Logout
@login_required(login_url='/login/')
def log_out(request):
    # Get first name of the user
    name = request.user.first_name
    logout(request)  # Logout
    return render(request, 'logout.html', {'name': name})

# Users
def users(request):
    User = get_user_model()  # Get custom user model
    Users = User.objects.all()  # Get all users
    return render(request, 'users.html', {'users': Users})

# Profile
@login_required(login_url='/login/')
def profile(request):
    return render(request, 'profile.html')

# Update Profile
@login_required(login_url='/login/')
def update_profile(request):
    # Get current user profile information
    form = forms.EditProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST':
        # Save profile form, set message and HTMX redirect to profile if the form is valid
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return HttpResponse(headers={'HX-Redirect': '/profile/'})
    # Render empty form if request is GET
    return render(request, 'partials/update_profile.html', {'form': form})

# Update Profile Picture
@login_required(login_url='/login/')
def update_picture(request):
    # Get current user profile picture
    form = forms.ProfilePictureForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST":
        if form.is_valid() and request.FILES:
            # Get and check file size
            print(request)
            print(request.FILES)
            print(request.FILES['profile_picture'])
            image = request.FILES['profile_picture']
            if image.size > 1 * 1024 * 1024:  # 1 MB
                messages.error(request, 'File size is too large. Max size is 1 MB'),
                return redirect("/profile/")  # Set error message and redirect to profile

            # Get current picture
            current_pic = request.user.profile_picture
            # Create a user special name
            special_name = "user_" + str(request.user.id) + "_" + current_pic.name

            # If there is current pic
            if current_pic:
                # 'profile_pics' folder needs to be added to the path because it is a post
                # request and django returns only the file name without whole path
                current_pic_path = os.path.join(settings.MEDIA_ROOT, "profile_pics", special_name)  # Get path
                # Remove if there is a file
                if os.path.isfile(current_pic_path):
                    os.remove(current_pic_path)

            # Save the form and set success message
            form.save()
            messages.success(request, 'Profile picture updated successfully.')
        else:
            # Set error message if form is not valid
            messages.error(request, 'Somethings went wrong :(')

        # Redirect to profile
        return redirect("/profile/")
    else:
        # Render current form if request is GET
        return render(request, 'partials/update_picture.html', {'form': form})

# Remove Profile Picture Query
@login_required(login_url='/login/')
def delete_or_cancel(request):
    return render(request, 'partials/delete_or_cancel.html')

# Remove Profile Picture
@login_required(login_url='/login/')
def remove_picture(request):
    # Get current picture
    current_pic = request.user.profile_picture
    # File name includes the path because it is a get request and django
    # returns the file name with the path on GET requests
    if current_pic and not current_pic.name == "profile_pics/default.png":  # If there is a picture and it is not default
        current_pic_path = os.path.join(settings.MEDIA_ROOT, current_pic.name)  # Get the path
        # Remove if there is a file
        if os.path.isfile(current_pic_path):
            os.remove(current_pic_path)

            # Set default picture
            request.user.profile_picture = "profile_pics/default.png"
            request.user.save()  # Save the user

            # Set success message and HTMX redirect to profile
            messages.success(request, 'Profile picture removed successfully')
            return HttpResponse(headers={'HX-Redirect': '/profile/'})
    # Return error message as HTTP response if there is no picture
    else:
        return HttpResponse("<p class='button-group' style='color:darkorange;font-size:18px'>Remove what?</p>")

# Cancel Action
@login_required(login_url='/login/')
def cancel_action(request):
    return HttpResponse("")  # Return empty HTTP response

# Dynamic User Profile
@login_required(login_url='/login/')
def user_profile(request, user_id):
    User = get_user_model()  # Get custom user model
    User = get_object_or_404(User, id=user_id)  # Get user from his/her id

    Posts = models.Post.objects.filter(author=User).order_by('-created_at')[:7]  # Get 7 latest posts of the user

    is_online = False
    if User.last_active:
        # is_online = True if user's last active is in last 5 mins
        is_online = (timezone.now() - User.last_active).total_seconds() < 300

    # Render user profile with the parameters
    return render(request, 'user_profile.html', {'user': User, 'is_online':is_online, 'posts': Posts})

# Dynamic User Posts
@login_required(login_url='/login/')
def user_posts(request, user_id):
    User = get_user_model()  # Get custom user model
    user = get_object_or_404(User, id=user_id)  # Get user from his/her id

    Posts = models.Post.objects.filter(author=user).order_by('-created_at')  # Get all posts of the user and order them

    # Pagination settings
    paginator = Paginator(Posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')  # Get the page number from the URL
    page_obj = paginator.get_page(page_number)  # Get the page object

    # Render user posts with the parameters
    return render(request, 'user_posts.html', {'user': user, 'page_obj': page_obj})

# Dashboard
@login_required(login_url='/login/')
def dashboard(request):
    sort_by = request.GET.get('sort', 'created_at')  # Get the sort parameter (created_at by default)
    order = request.GET.get('order', 'desc')  # Get the order parameter (desc by default)

    if order == 'desc':
        sort_by = f'-{sort_by}'  # Order the posts in descending order if the order parameter is 'desc'

    # Get all posts of the user and order them by the sort parameter
    Posts = models.Post.objects.filter(author=request.user).all().order_by(sort_by)

    # Send the posts, current sort and order to the template and render it
    context = {
        'posts': Posts,
        'current_sort': request.GET.get('sort', 'created_at'),
        'current_order': request.GET.get('order', 'desc'),
    }
    return render(request, 'dashboard.html', context)

# Add Category
@login_required(login_url='/login/')
def add_category(request):
    if request.method == "POST":
        # Get new category
        new_category = request.POST.get("new_category")
        if new_category:
            # Return error message as HTTP response if category already exists
            if models.Category.objects.filter(name=new_category).exists():
                return HttpResponse('''
                    <div id="message">
                        <div class="error-msg">This category already exists!</div>
                    </div>
                ''')
            # Create new category and return the option as selected with its id and name, if not exists
            else:
                category_, created = models.Category.objects.get_or_create(name=new_category, user=request.user)
                return HttpResponse(f'<option value="{category_.id}" selected>{category_.name}</option>')

        # Return error message as HTTP response if category name is empty
        else:
            return HttpResponse('''
                <div id="message">
                    <div class="error-msg">Category name cannot be empty!</div>
                </div>
            ''')
    else:
        return HttpResponse(status=400)  # Return bad request as HTTP response if method is not POST

# Add Tag
@login_required(login_url='/login/')
def add_tag(request):
    if request.method == "POST":
        # Get new tag
        new_tag = request.POST.get("new_tag")
        # If there is new tag
        if new_tag:
            # Return error message as HTTP response if tag already exists
            if models.Tag.objects.filter(name=new_tag).exists():
                return HttpResponse('''
                                    <div id="message">
                                        <div class="error-msg">This tag already exists!</div>
                                    </div>
                                ''')
            # Create new tag and return the option as selected with its id and name, if not exists
            else:
                tag_, created = models.Tag.objects.get_or_create(name=new_tag, user=request.user)
                return HttpResponse(f'''<option value="{tag_.id}" selected>{tag_.name}</option>''')

        # Return error message as HTTP response if tag name is empty
        else:
            return HttpResponse('''
                <div id="message">
                    <div class="error-msg">Tag name cannot be empty!</div>
                </div>
            ''')
    else:
        return HttpResponse(status=400)  # Return bad request as HTTP response if method is not POST

# Add Post
@login_required(login_url='/login/')
def add_post(request):
    if request.method == 'POST':
        form = forms.PostForm(request.POST)  # Get post form
        if form.is_valid():
            Post = form.save(commit=False)  # Create new post from the form without saving it

            # Set author, save the post and save the categories/tags (many to many fields)
            Post.author = request.user
            Post.save()
            form.save_m2m()

            # Show success message and redirect to dashboard
            messages.success(request, 'Post added successfully! Thank you ❤')
            return redirect('/dashboard/')

        # Show error message and render the form
        else:
            messages.error(request, 'Something went wrong :(')
            return render(request, 'partials/add_post.html', {'form': form})

    # If method is GET, render the form
    else:
        form = forms.PostForm()
        return render(request, 'partials/add_post.html', {'form': form})

# Edit Post
@login_required(login_url='/login/')
def edit_post(request, post_id):
    Post = models.Post.objects.get(id=post_id)  # Get the post by id
    if request.method == 'POST':
        form = forms.PostForm(request.POST, instance=Post)  # Get post form with the old form data
        if form.is_valid():
            form.save()  # Save the post
            form.save_m2m()  # Save the categories/tags (many to many fields)
            messages.success(request, 'Post edited successfully')  # Show success message

            # Redirect to dashboard
            return redirect('dashboard')

        # Show error message and render the form with the old form data and 'is_edit' flag
        else:
            messages.error(request, 'Something went wrong :(')
            return render(request, 'partials/add_post.html', {'form': form, 'is_edit': True})

    # If method is GET, render the form with the old form data, 'Post' object and 'is_edit' flag
    else:
        form = forms.PostForm(instance=Post)
        return render(request, 'partials/add_post.html', {'form': form, 'is_edit': True, 'post': Post})

# Delete Post
@login_required(login_url='/login/')
def delete_post(request, post_id):
    Post = models.Post.objects.get(id=post_id)  # Get the post by id
    Post.delete()  # Delete the post
    messages.success(request, 'Post deleted successfully')  # Show success message
    return redirect('dashboard')  # Redirect to dashboard

# Like Post
@login_required(login_url='/login/')
def like_post(request,post_id):
    post = get_object_or_404(models.Post, id=post_id)  # Get the post by id or return 404

    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)  # Remove user from likes if it exists in post's likes
    else:
        post.likes.add(request.user)  # Add user to post's likes

    # Create a dynamic URL using the reverse function
    url = reverse("like_post", args=[post.id])

    # Return the HTMX button with the number of likes and the URL as HTTP response
    return HttpResponse(f'''
            <button class="like-btn" hx-get="{url}" hx-trigger="click" hx-swap="outerHTML">
                ❤<span class="num"> {post.total_likes()}</span>
            </button>
        ''')

# Like comment
@login_required(login_url='/login/')
def like_comment(request, pk):
    comment = get_object_or_404(models.Comment, pk=pk)  # Get the comment by primary key or return 404

    if comment.likes.filter(id=request.user.id).exists():
        comment.likes.remove(request.user)  # Remove user from likes if it exists in comment's likes
    else:
        comment.likes.add(request.user)  # Add user to comment's likes

    # Return the number of likes as HTTP response
    return HttpResponse(comment.total_likes())

# All Posts
@login_required(login_url='/login/')
def posts(request):
    # Get all published posts and sort them by created_at in descending order
    Posts = models.Post.objects.order_by('-created_at')
    paginator = Paginator(Posts, 10)  # 10 posts per page by using Paginator

    page_number = request.GET.get('page')  # Get the page number from the URL
    page_obj = paginator.get_page(page_number)  # Get the page object

    # Render the posts page with the page object
    return render(request, 'posts.html', {'page_obj': page_obj})

# Post Detail
@login_required(login_url='/login/')
def post_detail(request, post_id):
    Post = get_object_or_404(models.Post, id=post_id)  # Get the post by id or return 404
    comments_list = Post.comments.all().order_by('-created_at')  # Get all comments of the post and sort them by created_at

    paginator = Paginator(comments_list,3)  # 3 comments per page by using Paginator
    page_number = request.GET.get('page')  # Get the page number from the URL
    Comments = paginator.get_page(page_number)  # Get the page object of comments

    if request.method == 'POST':
        form = forms.CommentForm(request.POST)  # Get comment form
        if form.is_valid():
            comment = form.save(commit=False)  # Get the comment form without saving it
            comment.post = Post  # Set the post of the comment
            comment.user = request.user  # Set the user of the comment

            comment_data = form.cleaned_data['content']  # Get the content of the comment
            hashtags = re.findall(r'#\w+', comment_data)  # Find all hashtags in the comment with regex
            comment.save()  # Save the comment

            # Check if there is a tag that is longer than 15 characters
            invalid = False
            for tag in hashtags:
                if len(tag) > 15:
                    invalid = True
                    break

            # If there is no invalid tag, create or get the tag, remove the tag from the comment,
            # add the tag to the comment's tags, and save the comment
            if not invalid:
                comment.save()
                for tag in hashtags:
                    tag_name = tag[1:]
                    tag_obj, created = models.Tag.objects.get_or_create(name=tag_name, user=request.user)
                    comment_data = comment_data.replace(tag, "")
                    comment.content = comment_data
                    comment.tags.add(tag_obj)
                    comment.save()

            # If there is an invalid tag, show an error message and redirect to the post detail page
            # with reverse function and the post id with from=comments query parameter (for page scrolling)
            else:
                messages.error(request, 'Tag name cannot be longer than 15 characters')
                url = reverse('post_detail', args=[post_id])
                return redirect(f'{url}?from=comments')

            comment.save()
            form.save_m2m()
            url = reverse('post_detail', args=[post_id])
            return redirect(f'{url}?from=comments')

    else:
        # If the request method is not POST, create an empty form
        form = forms.CommentForm()

    # Render the post detail page with the post, comments, and form parameters
    return render(request, 'post_detail.html', {
        'post': Post,
        'comments': Comments,
        'form': form
    })

# Full Content View for Read More action
@login_required(login_url='/login/')
def full_content(request, post_id):
    Post = get_object_or_404(models.Post, id=post_id)
    return render(request, 'partials/full_content.html', {'post': Post})

# All Categories
def categories(request):
    # Get all categories, count the number of posts in each category with Count(), add the count to each
    # category object with annotate(), and order them by the number of posts in descending order
    Categories = models.Category.objects.annotate(Count('posts')).order_by('-posts__count')

    # Delete categories that have no posts
    for category in Categories:
        if models.Post.objects.filter(categories=category).count() == 0:
            category.delete()

    paginator = Paginator(Categories, 10)  # 10 categories per page by using Paginator

    page_number = request.GET.get('page')  # Get the page number from the URL
    items = paginator.get_page(page_number)  # Get the page object of categories
    print(items)
    # Render the categories page with the page object
    return render(request, 'categories.html', {'items': items})

# Delete Category
@login_required
def category_delete(request, pk):
    # Get the category by pk and user or return 404
    Category = get_object_or_404(models.Category, pk=pk, user=request.user)

    # Check if the category is used by other users
    if models.Post.objects.filter(categories=Category).exclude(author=request.user).exists():
        # Show an error message if so
        messages.error(request, "This category is used by other users! Do not delete it!")

    else:
        # Delete the category and show a success message
        Category.delete()
        messages.success(request, "Category deleted successfully.")

    # Redirect to the categories page
    return redirect('/categories/')

# Edit Category
@login_required
def category_edit(request, pk):
    # Get the category by pk and user or return 404
    Category = get_object_or_404(models.Category, pk=pk, user=request.user)
    if request.method == 'POST':
        new_name = request.POST.get('name')  # Get the name from the form

        # If the new name is not empty
        if new_name:

            # Check if the new name already exists
            if models.Category.objects.filter(name=new_name).exclude(pk=Category.pk).exists():

                # Return an error message in a div as HTTP response if so
                return HttpResponse(f'<div class= "error" id="name-{Category.pk}">Category already exists!</div>')

            else:
                Category.name = new_name  # Set the name of the category
                Category.save()  # Save the category

                # Return the name of the category in a link as HTTP response
                return HttpResponse(f'<a href= "/category_detail-{Category.pk}/" class="name" id="name-{Category.pk}">{Category.name}</a>')

        else:
            # Return an error message in a div as HTTP response if the new name is empty
            return HttpResponse(f'<div class= "error" id="name-{Category.pk}">Empty is not allowed!</div>')

    else:
        # Render the edit category page with the category if the request method is GET
        return render(request, 'partials/edit_category.html', {'category': Category})

# Category Detail
@login_required(login_url='/login/')
def category_detail(request, pk):
    Category = get_object_or_404(models.Category, pk=pk)  # Get the category by pk or return 404

    # Get all posts in the category and order them by created_at in descending order
    Posts = models.Post.objects.filter(categories=Category).order_by('-created_at')

    paginator = Paginator(Posts, 10)  # 10 posts per page by using Paginator
    page_number = request.GET.get('page')  # Get the page number from the URL
    page_obj = paginator.get_page(page_number)  # Get the page object of posts

    # Render the category detail page with the category and page object
    return render(request, 'category_detail.html', {'category': Category, 'page_obj': page_obj})

# Tag Detail
@login_required(login_url='/login/')
def tag_detail(request, pk):
    Tag = get_object_or_404(models.Tag, pk=pk)  # Get the tag by pk or return 404

    # Get all posts and comments of the tag and order them by created_at in descending order
    Posts = models.Post.objects.filter(tags=Tag).order_by('-created_at')
    Comments = models.Comment.objects.filter(tags=Tag).order_by('-created_at')

    # Combine the posts and comments into a single list by
    # representing each post as a dictionary with a 'type' key and an 'item' value as the post/comment object

    # Add 2 lists to the 'items' list and sort them by 'created_at' in descending order
    items = [{'type': 'post', 'item': post} for post in Posts] + [{'type': 'comment', 'item': Comment} for Comment in Comments]
    items.sort(key=lambda x: x['item'].created_at, reverse=True)

    paginator = Paginator(items, 10)  # 10 posts per page by using Paginator
    page_number = request.GET.get('page')  # Get the page number from the URL
    page_obj = paginator.get_page(page_number)  # Get the page object of posts

    # Render the tag detail page with the tag and page object
    return render(request, 'tag_detail.html', {'tag': Tag, 'page_obj': page_obj})

# All Tags
def tags(request):
    # Get all tags and order them by total_count in descending order using annotate()
    Tags = models.Tag.objects.annotate(total_count=Count('posts') + Count('comments')).order_by('-total_count')

    # Delete tags that have no posts and comments
    for tag in Tags:
        if models.Post.objects.filter(tags=tag).count() == 0 and \
                models.Comment.objects.filter(tags=tag).count() == 0:
            tag.delete()

    paginator = Paginator(Tags, 10)  # 10 posts per page by using Paginator
    page_number = request.GET.get('page')  # Get the page number from the URL
    items = paginator.get_page(page_number)  # Get the page object of tags

    # Render the tags page with the page object
    return render(request, 'tags.html', {'items': items})

# Edit Tag
@login_required(login_url='/login/')
def tag_edit(request, pk):
    # Get the tag by pk and user or return 404
    Tag = get_object_or_404(models.Tag, pk=pk, user=request.user)
    if request.method == 'POST':
        new_name = request.POST.get('name')  #

        # If the new name is not empty
        if new_name:
            # Check if the new name already exists
            if models.Tag.objects.filter(name=new_name).exclude(pk=Tag.pk).exists():

                # Return an error message in a div as HTTP response if so
                return HttpResponse(
                    f'<div class= "error" id="name-{Tag.pk}">Tag already exists!</div>')

            # If the new name does not exist
            else:
                Tag.name = new_name  # Update the name of the tag
                Tag.save()  # Save the changes

                # Return the new name in a link as HTTP response if so
                return HttpResponse(
                    f'<a href= "/tag_detail-{Tag.pk}/" class="name" id="name-{Tag.pk}">{Tag.name}</a>')
        else:
            # Return an error message in a div as HTTP response if the new name is empty
            return HttpResponse(f'<div class= "error" id="name-{Tag.pk}">Empty is not allowed!</div>')

    else:
        # Render the edit tag page with the tag if the request method is GET
        return render(request, 'partials/edit_tag.html', {'tag': Tag})

# Delete Tag
@login_required(login_url='/login/')
def tag_delete(request, pk):
    # Get the tag by pk and user or return 404
    Tag = get_object_or_404(models.Tag, pk=pk, user=request.user)

    # Check if the tag is used by other users
    if models.Post.objects.filter(tags=Tag).exclude(author=request.user).exists():

        # Show error message and redirect to the tags page if so
        messages.error(request, "This tag is used by other users! Do not delete it!")
        return redirect('tags')

    else:
        # Delete the tag and show success message and redirect to the tags page if not
        Tag.delete()
        messages.success(request, "Tag deleted successfully.")
        return redirect('tags')

# All Comments
@login_required(login_url='/login/')
def comments(request):
    # Get all comments and order them by created_at in descending order
    comments_list = models.Comment.objects.all().order_by('-created_at')

    paginator = Paginator(comments_list, 10)  # 10 posts per page by using Paginator
    page_number = request.GET.get('page')  # Get the page number from the URL
    Comments = paginator.get_page(page_number)  # Get the page object of comments

    # Render the comments page with the page object
    return render(request, 'comments.html', {'comments': Comments})

# Edit Comment
@login_required(login_url='/login/')
def edit_comment(request, pk):
    # Get the comment by pk and user or return 404
    comment = get_object_or_404(models.Comment, pk=pk, user=request.user)

    # If the request method is POST
    if request.method == 'POST':
        new_comment = request.POST.get('content')  # Get the new comment

        # If the new comment is not empty
        if new_comment:

            hashtags = re.findall(r'#\w+', new_comment)  # Find all hashtags in the comment with regex

            # Check if there is a tag that is longer than 15 characters
            invalid = False
            for tag in hashtags:
                if len(tag) > 15:
                    invalid = True
                    break

            # If there is no tag that is longer than 15 characters
            if not invalid:
                comment.tags.clear()  # Clear current the tags of the comment

                # Add new tags to the comment's tags field and remove the tags from the comment content
                for tag in hashtags:
                    tag_name = tag[1:]
                    tag_obj, created = models.Tag.objects.get_or_create(name=tag_name, user=request.user)
                    new_comment = new_comment.replace(tag, "")
                    comment.tags.add(tag_obj)

                # Update the comment's content and save it
                comment.content = new_comment
                comment.save()

                # Get all the tags of the comment and convert them to HTML links, store in tags_html variable
                tags_html = ''.join(
                    [f'<a href="{reverse("tag_detail", args=[tag.pk])}">#{tag.name}</a>' for tag in comment.tags.all()])

                # Create the response HTML with the comment content, id and tags
                response_html = f'''
                    <div class="comment-content-2" id="name-{comment.pk}">
                        {comment.content}
                        {tags_html}
                    </div>
                    '''

                # Return the response HTML as HTTP response
                return HttpResponse(response_html)

            else:
                # Return an error message in a div as HTTP response if the new name is longer than 15 characters
                return HttpResponse(f'<div class= "error" id="name-{comment.pk}">Tag is too long! The maximum is 15 characters...</div>')
        else:
            # Return an error message in a div as HTTP response if the new name is empty
            return HttpResponse(f'<div class= "error" id="name-{comment.pk}">Empty is not allowed!</div>')
    else:
        # Render the edit comment page with the comment if the request method is GET
        return render(request, 'partials/edit_comment.html', {'comment': comment})

# Delete Comment
@login_required(login_url='/login/')
def delete_comment(request, pk):
    # Get the comment by pk and user or return 404
    comment = get_object_or_404(models.Comment, pk=pk, user=request.user)

    comment.delete()  # Delete the comment
    messages.success(request, 'Comment deleted successfully')  # Show success message

    # Get the URL of comment's post with reverse() and redirect to it with from=comments parameter
    url = reverse('post_detail', args=[comment.post.id])
    return redirect(f'{url}?from=comments')

# Account Settings
@login_required(login_url='/login/')
def account_settings(request):
    return render(request, "partials/settings.html")

# Change Email
@login_required(login_url='/login/')
def change_email(request):
    # If the request method is POST
    if request.method == 'POST':
        # Get the new email from the form
        new_email = request.POST.get('email')

        request.user.email = new_email  # Set the new email for the current user
        request.user.save()  # Save the user
        messages.success(request, "Email updated successfully!")  # Show success message
        return redirect("/profile/")  # Redirect to profile

    else:
        # Return a 400 error if the request method is not POST
        return HttpResponse(status=400)

# Delete Account
@login_required(login_url='/login/')
def delete_account(request):
    name = request.user.first_name  # Get the first name of the user
    request.user.delete()  # Delete the user
    messages.success(request, f"Your account deleted successfully, goodbye {name} ❤")  # Show success message
    return HttpResponse(headers={'HX-Redirect': '/'})  # HTMX redirect to index page

# CSRF Failure
def csrf_failure(request, reason=""):
    # Return an error message as an HTTP response
    return HttpResponse("<p class='error'>An issue occurred. Please reload the page and try again</p>")

