from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
import uuid
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password

# PROFILE MODEL
class Profile(models.Model):
    """
    Extended user profile with social links, bio, and visibility settings.
    Each user has exactly one profile.
    """
    
    # Profile Visibility Choices
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('followers', 'Followers Only'),
        ('private', 'Private'),
    ]
    
    # Core Relationships
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    # Personal Information
    name = models.CharField(max_length=150, blank=True, null=True)
    bio = models.TextField(max_length=300, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profiles/',
        default='default_pic.png',
        blank=True,
        null=True
    )
    
    # Social Media Links
    website = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    
    # Privacy Settings
    profile_visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='public'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.username

    @property
    def age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            today = timezone.now().date()
            return (
                today.year - self.date_of_birth.year - (
                    (today.month, today.day) < 
                    (self.date_of_birth.month, self.date_of_birth.day)
                )
            )
        return None


# CATEGORY MODEL
class Category(models.Model):
    """Blog post categories for organizing content"""
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)



# TAG MODEL
class Tag(models.Model):
    """Flexible tags for blog posts"""
    
    name = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)



# BLOG MODEL
class Blog(models.Model):
    """Main blog post model with content, metadata, and engagement tracking"""
    
    # Primary Key & Core Relationships
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name='blogs'
    )
    
    # Content
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='blogs'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='blogs')
    
    # Media
    image = models.ImageField(upload_to='blogs/', blank=True, null=True)
    excerpt = models.CharField(max_length=300, blank=True)
    content = models.TextField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not provided"""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def like_count(self):
        """Count of likes for this blog post"""
        return self.likes.count()

    @property
    def comment_count(self):
        """Count of comments for this blog post"""
        return self.comments.count()
    
    @property
    def view_count(self):
        """Count of views for this blog post"""
        return self.views.count()



# COMMENT MODEL
class Comment(models.Model):
    """Nested comment system with reply functionality"""
    
    # Relationships
    blog = models.ForeignKey(
        Blog, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE, 
        related_name='replies'
    )
    
    # Content
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_at']  # Chronological order for better thread display

    def __str__(self):
        return f'{self.user.username} on {self.blog.title}'

    def children(self):
        """Get all approved replies to this comment"""
        return self.replies.filter(is_approved=True)

    @property
    def is_parent(self):
        """Check if this is a top-level comment (not a reply)"""
        return self.parent is None



# LIKE MODEL
class Like(models.Model):
    """Track user likes on blog posts"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='likes'
    )
    blog = models.ForeignKey(
        Blog, 
        on_delete=models.CASCADE, 
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blog')  # Prevent duplicate likes
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} liked {self.blog.title}'


# USER EMAIL MODEL
class UserEmail(models.Model):
    """Manage multiple email addresses for a user with verification status"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='emails'
    )
    email = models.EmailField(unique=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} ({'Verified' if self.verified else 'Unverified'})"



# EMAIL OTP MODEL
class EmailOTP(models.Model):
    """
    One-time password system for email verification.
    Stores hashed codes for security.
    """
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='email_otps'
    )
    email = models.EmailField()  # Target email address
    
    # Security
    code_hash = models.CharField(max_length=255)  # Hashed OTP (never store plaintext)
    
    # Timestamps & Limits
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=5)
    verified = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'email']),
        ]

    def set_code(self, code_plain):
        """Hash and store the OTP code"""
        self.code_hash = make_password(code_plain)

    def verify_code(self, code_plain):
        """
        Verify the provided OTP code against stored hash
        Returns: (success: bool, message: str)
        """
        # Increment attempts when called
        self.attempts += 1
        
        # Check attempt limits
        if self.attempts > self.max_attempts:
            return False, 'max_attempts_exceeded'
        
        # Check expiry
        if timezone.now() > self.expires_at:
            return False, 'expired'
        
        # Verify code
        valid = check_password(code_plain, self.code_hash)
        if valid:
            self.verified = True
            return True, 'verified'
        
        return False, 'invalid'



# FOLLOW MODEL
class Follow(models.Model):
    """User following system with approval for private accounts"""
    
    follower = models.ForeignKey(
        User, 
        related_name='following', 
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        User, 
        related_name='followers', 
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Approval system for private accounts
    is_approved = models.BooleanField(default=True)

    class Meta:
        unique_together = ('follower', 'following')  # Prevent duplicate follows
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"


# =============================================================================
# NOTIFICATION MODEL
# =============================================================================
class Notification(models.Model):
    """System for user notifications across different activities"""
    
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('reply', 'Reply'),
        ('follow', 'Follow'),
        ('follow_request', 'Follow Request'),
        ('trending', 'Trending'),
    ]
    
    # Relationships
    sender = models.ForeignKey(
        User, 
        related_name='sent_notifications', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    recipient = models.ForeignKey(
        User, 
        related_name='notifications', 
        on_delete=models.CASCADE
    )
    
    # Notification Content
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.CharField(max_length=255)
    
    # Optional Object References
    blog = models.ForeignKey(
        'Blog', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    comment = models.ForeignKey(
        'Comment', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    follow = models.ForeignKey(
        'Follow', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    
    # Status & Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification to {self.recipient.username} - {self.notification_type}"