from django import template
from blog.models import Follow

register = template.Library()

@register.filter
def is_following(target_user, current_user):
    """Check if current_user follows target_user."""
    return Follow.objects.filter(
        follower=current_user,
        following=target_user,
        is_approved=True
    ).exists()

@register.filter
def has_pending_request(target_user, current_user):
    """Check if current_user has sent a pending follow request."""
    return Follow.objects.filter(
        follower=current_user,
        following=target_user,
        is_approved=False
    ).exists()