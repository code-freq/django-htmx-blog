# Django-HTMX Blog

## Description

Django-HTMX Blog is a dynamic and interactive blog platform built with Django and HTMX. Designed to offer an engaging user experience, this project allows users to create, edit, and manage blog posts, organizing them with categories and tags, and engaging with posts through comments and likes.

Leveraging HTMX, the platform provides real-time updates, enabling users to interact with content without reloading the entire page. This lightweight yet powerful integration enhances speed and interactivity, creating a smoother and more enjoyable blogging experience.

## Features

- Create, edit, and delete blog posts
- Create, edit, and delete categories and tags
- Create, edit, and delete comments
- Add likes to posts and comments
- Home page:
  - Most liked and commented posts
  - Most used categories and tags
- User profiles and post history:
  - Username, Name and Surname
  - Profile picture
  - Bio
  - Last active / Joined on status
  - Online / Offline indicator
  - Latest Posts
- Update and remove profile picture
- Edit profile information
- Account settings:
  - Edit email and password
  - Delete account
- HTMX integration for real-time content updates without page reloads


## Requirements

- **Django**==5.1.2
- **django-ckeditor**==6.7.1
- **pillow**==11.0.0

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/code-freq/django-htmx-blog.git
    ```
2. Navigate to the GitHub project directory:
    ```bash
    cd django-htmx-blog
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Navigate to the main project directory:
    ```bash
    cd weblog_project
    ```

5. Run database migrations:
    ```bash
    python manage.py migrate
    ```

6. Create a superuser account (for admin account):
    ```bash
    python manage.py createsuperuser
    ```

7. Create an old_user account (necessary):
    ```bash
    python manage.py shell
    ```
    ```
    from django.contrib.auth import get_user_model
    ```
    ```
    User = get_user_model()
    ```
    ```
    User.objects.create_user(
        username="old_user",
        first_name="Old",
        last_name="User",
        email="olduser@example.com",
        password="password",
        id=14
    )
    ```

## Usage

1. **Run the development server:**
    ```bash
    python manage.py runserver
    ```
2. **Access the application:**
    - Open a web browser and go to http://localhost:8000

3. **Usage instructions:**
    - **Home Page:** Explore trending content, including the most used categories / tags and most liked and commented posts.
    - **Users:** View a list of all registered users and access their profiles.
    - **Posts:** Browse through all blog posts available on the platform.
    - **Categories and Tags:** Access and explore all categories and tags; edit or delete the ones you’ve created.
    - **Dashboard:** From your dashboard, add new posts, manage them by editing or deleting them as needed.
    - **Profile:** Click on your username to view and update your profile.
    - **Account Settings:** Click on the account settings from your profile to update your email and password, or delete your account.

## Contact
For questions, feedback, or collaboration inquiries, feel free to reach out:
- **Email:** *code.freq7@gmail.com*
- **GitHub:** [https://github.com/code-freq](https://github.com/code-freq)