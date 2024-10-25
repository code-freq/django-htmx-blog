from .models import Post, Category, Tag, Comment, CustomUser
from django.template.response import TemplateResponse
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.db.models import Count
from django.contrib import admin
from django.urls import path

# Register your models here to make them appear in the admin panel.

# Register Post model
@admin.register(Post)  # Register Post model
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_at', 'total_likes')  # fields of posts to display
    search_fields = ('title', 'content', 'total_likes')  # fields of posts to search
    list_filter = ('categories', 'tags')  # fields of posts to filter
    raw_id_fields = ('author',)  # add search bar for author id instead of select box
    filter_horizontal = ('categories', 'tags')  # display horizontal filter interface for categories and tags
    ordering = ('-created_at',)  # sort posts by creation date (newer first)
    readonly_fields = ('created_at', 'updated_at')  # disable editing of created_at and updated_at
    date_hierarchy = 'created_at'  # display date hierarchy according to creation date

    # Display the total likes in admin
    def total_likes(self, obj):
        return obj.total_likes()

    total_likes.admin_order_field = 'likes'  # Allow sorting by the 'likes' field in total_likes column
    total_likes.short_description = 'Likes'  # Change 'likes' to 'Likes'

    class Media:
        css = {
            'all': ('css/admin/posts.css',)  # Custom CSS for admin styling using posts.css
        }

# Register Comment model
@admin.register(Comment)  # Register Comment model
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'content', 'created_at', 'updated_at', 'total_likes')

    # Display the total likes in admin
    def total_likes(self, obj):
        return obj.total_likes()

    total_likes.admin_order_field = 'likes'  # Allow sorting by the 'likes' field in total_likes column
    total_likes.short_description = 'Likes'  # Change 'likes' to 'Likes'

    class Media:
        css = {
            'all': ('css/admin/users.css',)  # Custom CSS for admin styling using users.css
        }

# Custom CustomUser model to display id and bio on admin panel
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'bio', 'last_active')
    list_filter = ('is_staff', 'is_superuser')
    ordering = ('-username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'bio', 'profile_picture')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_active', 'last_login', 'date_joined')}),
    )

    class Media:
        css = {
            'all': ('css/admin/users.css',)  # Custom CSS for admin styling using users.css
        }

# CategoryAdmin
@admin.register(Category)  # Register Category model
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_link', 'user', 'post_count')
    search_fields = ('user',)
    actions = ['view_related_posts']

    def get_queryset(self, request):
        # Get the queryset from the parent class
        queryset = super().get_queryset(request)
        # Count the total 'posts' using Count() and add it to the 'post_count' field using annotate()
        queryset = queryset.annotate(post_count=Count('posts'))
        return queryset  # return the queryset

    # Display the total posts in admin and make it available to sort by post_count
    @admin.display(ordering='post_count')
    def post_count(self, obj):
        return obj.post_count  # Use the 'post_count' field comes from annotate()

    post_count.short_description = 'Number of Posts'  # Change 'post_count' to 'Number of Posts'

    # Display all posts of a category
    def view_posts(self, request, category_id):
        category = Category.objects.get(id=category_id)  # Get the category by id
        posts = category.posts.all()  # Get all posts of it

        # Render the category posts page with the category and posts
        context = dict(
            self.admin_site.each_context(request),
            posts=posts,
            category=category,
        )
        # Return the category posts page using TemplateResponse()
        return TemplateResponse(request, "admin/category_posts.html", context)

    # Make the category name clickable and make it available to sort by name
    @admin.display(ordering='name')
    def name_link(self, obj):
        # Return a link to the category name using format_html()
        return format_html('<a href="{}">{}</a>', f'posts/{obj.id}', obj.name)

    name_link.short_description = 'Category Name'  # Change 'name' to 'Category Name'

    # Add a custom url for the category posts page
    def get_urls(self):
        urls = super().get_urls()  # Get the urls from the parent class

        # Add a custom url for the category posts page
        custom_urls = [
            path('posts/<int:category_id>/', self.admin_site.admin_view(self.view_posts), name="category_posts"),
        ]
        # Add the custom urls to the urls and return them
        return custom_urls + urls

# TagAdmin
@admin.register(Tag)  # Register Tag model
class TagAdmin(admin.ModelAdmin):
    list_display = ('name_link', 'user', 'post_count', 'comment_count')
    search_fields = ('name', 'user')

    def get_queryset(self, request):
        # Get the queryset from the parent class
        queryset = super().get_queryset(request)

        # Count the total 'posts' and 'comments' using Count() and add it to the 'post_count'
        # and 'comment_count' fields using annotate()
        queryset = queryset.annotate(
            post_count=Count('posts'),
            comment_count=Count('comments')
        )
        return queryset  # Return the queryset

    # Display the total posts in admin and make it available to sort by post_count
    @admin.display(ordering='post_count')
    def post_count(self, obj):
        return obj.post_count  # Use the 'post_count' field comes from annotate()

    post_count.short_description = 'Number of Posts'  # Change 'post_count' to 'Number of Posts'

    # Display the total comments in admin and make it available to sort by comment_count
    @admin.display(ordering='comment_count')
    def comment_count(self, obj):
        return obj.comment_count  # Use the 'comment_count' field comes from annotate()

    comment_count.short_description = 'Number of Comments'  # Change 'comment_count' to 'Number of Comments'

    # Make the category name clickable and make it available to sort by name
    @admin.display(ordering='name')
    def name_link(self, obj):
        # Return a link to the category name using format_html()
        return format_html('<a href="{}">{}</a>', f'posts_comments/{obj.id}', obj.name)

    name_link.short_description = 'Tag Name'  # Change 'name' to 'Tag Name'

    # Display all posts comments of a category
    def view_posts_comments(self, request, tag_id):
        tag = Tag.objects.get(id=tag_id)   # Get the tag by id
        posts = tag.posts.all()  # Get all posts of it
        comments = Comment.objects.filter(post__tags=tag)  # Get all comments of it

        # Render the tag_posts_comments page with the tag, posts and comments
        context = dict(
            self.admin_site.each_context(request),
            posts=posts,
            comments=comments,
            tag=tag,
        )
        # Return the tag posts & comments page using TemplateResponse()
        return TemplateResponse(request, "admin/tag_posts_comments.html", context)

    # Add a custom url for the tag posts & comments page
    def get_urls(self):
        urls = super().get_urls()  # Get the urls from the parent class

        # Add a custom url for the tag posts & comments page
        custom_urls = [
            path('posts_comments/<int:tag_id>/', self.admin_site.admin_view(self.view_posts_comments),
                 name="tag_posts_comments"),
        ]
        # Add the custom urls to the urls and return them
        return custom_urls + urls
