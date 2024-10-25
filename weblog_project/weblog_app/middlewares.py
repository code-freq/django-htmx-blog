from django.utils import timezone

# Middlewares runs on every request, they run between requests and responses

# Middleware for updating user's "last active" every 5 mins
class UpdateLastActiveMiddleware:
    # Initialize the middleware with 'get_response' handler when it is created
    def __init__(self, get_response):
        self.get_response = get_response

    # Execute method for each request passing through the middleware
    def __call__(self, request):

        # Update if user is logged in
        if request.user.is_authenticated:

            # Update if user has no "last active" or has "last active" older than 5 mins
            if not request.user.last_active or (timezone.now() - request.user.last_active).total_seconds() > 300:

                # Update user's "last active"
                request.user.last_active = timezone.now()
                request.user.save(update_fields=['last_active'])

        # Pass the request to the next layer of middleware or the view and get the response
        response = self.get_response(request)
        return response

