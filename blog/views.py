from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import *
from django.db.models import Count
import json
from django.db.models import Sum, Count
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.db.models import F
from django.utils.safestring import mark_safe
from datetime import timedelta, date
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from .models import UserEmail
from .utils import create_and_send_otp
from django.core.mail import send_mail
import random
from django.db.models import Q

@login_required
def create_or_edit_profile(request):
    # Try to get existing profile for the logged-in user
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)

    if request.method == 'POST':
        # Get all fields from POST normally
        profile.username = request.POST.get('username') or request.user.username
        profile.name = request.POST.get('name')
        profile.bio = request.POST.get('bio')
        profile.date_of_birth = request.POST.get('dob')
        profile.github = request.POST.get('github')
        profile.twitter = request.POST.get('twitter')
        profile.instagram = request.POST.get('instagram')
        profile.linkedin = request.POST.get('linkedin')
        profile.website = request.POST.get('website')

        # Handle profile picture if uploaded
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        # Save it normally
        profile.save()
        return redirect('profile')

    # Render form with existing profile data
    return render(request, 'blog/create_profile.html', {'profile': profile})


@login_required
def profile_view(request):
    profile = request.user.profile
    user_obj = request.user  # This is key

    followers_count = Follow.objects.filter(following=user_obj, is_approved=True).count()
    following_count = Follow.objects.filter(follower=user_obj, is_approved=True).count()

    return render(request, 'blog/view_profile.html', {
        'profile': profile,
        'followers_count': followers_count,
        'following_count': following_count,
    })


@login_required
def update_profile(request):
    """Handles displaying and updating the user's profile."""
    profile = request.user.profile  # Assuming OneToOne relation with User

    # Define this first so it's always available (GET or POST)
    social_fields = ["github", "twitter", "linkedin", "instagram"]

    if request.method == "POST":
        # Get fields from the POST data
        profile.name = request.POST.get("name")
        profile.bio = request.POST.get("bio")
        profile.date_of_birth = request.POST.get("dob") or None
        profile.github = request.POST.get("github")
        profile.twitter = request.POST.get("twitter")
        profile.instagram = request.POST.get("instagram")
        profile.linkedin = request.POST.get("linkedin")
        profile.website = request.POST.get("website")

        # Handle uploaded profile picture (if any)
        if "profile_picture" in request.FILES:
            profile.profile_picture = request.FILES["profile_picture"]

        # Save profile data
        profile.save()

        # Optional: Give user feedback
        from django.contrib import messages
        messages.success(request, "Your profile has been updated successfully!")

        # Redirect to the profile page (or any page you like)
        return redirect("profile")

    # GET request → render the edit form
    return render(
        request,
        "blog/update_profile.html",
        {"profile": profile, "social_fields": social_fields},
    )

def dashboard_view(request):
    return render(request, 'blog/dashboard.html')

@login_required
def blog(request):
    # Fetch all published blogs
    all_blogs = Blog.objects.filter(is_published=True).select_related('author', 'author__user', 'category').prefetch_related('tags')

    visible_blogs = []

    for blog_post in all_blogs:
        profile = blog_post.author  # Profile object
        user_obj = profile.user     # User object

        # Public profiles → everyone sees
        if profile.profile_visibility == 'public':
            visible_blogs.append(blog_post)
        elif profile.profile_visibility == 'followers':
            if request.user.is_authenticated and (
                request.user.id == profile.user.id or Follow.objects.filter(follower=request.user, following=profile.user, is_approved=True).exists()):
                visible_blogs.append(blog_post)
            elif profile.profile_visibility == 'private':
                if request.user.is_authenticated and request.user.id == profile.user.id:
                    visible_blogs.append(blog_post)

    # Annotate counts
    for blog_post in visible_blogs:
        blog_post.num_likes = blog_post.likes.count()
        blog_post.num_comments = blog_post.comments.count()
    

    categories = Category.objects.all()
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()

    return render(request, 'blog/blogs.html', {'blogs': visible_blogs, 'categories': categories, 'notifications': notifications,'unread_count': unread_count})

@require_POST
def increment_blog_view(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, is_published=True)

    if request.user.is_authenticated and blog.author.user == request.user:
        return JsonResponse({'status': 'skipped', 'views': blog.views})

    session_key = f"viewed_blog_{blog.id}"
    if not request.session.get(session_key, False):
        Blog.objects.filter(id=blog.id).update(views=F('views') + 1)
        request.session[session_key] = True
        blog.refresh_from_db(fields=['views'])
        return JsonResponse({'status': 'incremented', 'views': blog.views})

    return JsonResponse({'status': 'already_viewed', 'views': blog.views})

@login_required
def tag_suggestions(request):
    tags = list(Tag.objects.values_list('name', flat=True))
    return JsonResponse(tags, safe=False)

@login_required
def category_suggestions(request):
    categories = list(Category.objects.values_list('name', flat=True))
    return JsonResponse(categories, safe=False)

@login_required
def create_blog(request):
    categories = Category.objects.all()

    if request.method == "POST":
        title = request.POST.get("title")
        category_id = request.POST.get("category")
        excerpt = request.POST.get("excerpt", "")
        content = request.POST.get("content")
        is_published = bool(request.POST.get("is_published"))
        image = request.FILES.get("image")
        tags_input = request.POST.get("tags", "[]")

        # Parse Tagify input (JSON string)
        try:
            tags_list = [t["value"].strip() for t in json.loads(tags_input) if t["value"].strip()]
        except json.JSONDecodeError:
            tags_list = []

        # Validate required fields
        if not title or not content or not category_id:
            return render(request, "blog/create_blog.html", {
                "categories": categories,
                "error": "Please fill in all required fields.",
            })

        # Get category object
        category_input = request.POST.get("category", "")
        try:
            category_data = json.loads(category_input)
            category_name = category_data[0]["value"].strip() if category_data else ""
        except json.JSONDecodeError:
            category_name = category_input.strip()

        if not category_name:
            return render(request, "blog/create_blog.html", {
                "categories": Category.objects.all(),
                "error": "Please enter a category.",
            })

        category, _ = Category.objects.get_or_create(name=category_name, defaults={'slug': slugify(category_name)})

        # Create blog
        blog = Blog.objects.create(
            author=request.user.profile,
            title=title,
            category=category,
            excerpt=excerpt,
            content=content,
            image=image,
            is_published=is_published,
            slug=slugify(title)
        )

        # Handle tags (auto-create if not exist)
        for tag_name in tags_list:
            tag, _ = Tag.objects.get_or_create(name=tag_name, defaults={'slug': slugify(tag_name)})
            blog.tags.add(tag)

        return redirect("blogs")  # redirect wherever you want after publishing

    # GET request (load form)
    return render(request, "blog/create_blog.html", {
        "categories": categories
    })

@login_required
def edit_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug, author=request.user.profile)
    categories = Category.objects.all()
    tags = list(blog.tags.values_list('name', flat=True))  # ✅ define early

    if request.method == 'POST':
        blog.title = request.POST.get('title')
        blog.content = request.POST.get('content')
        blog.is_published = 'is_published' in request.POST

        category_id = request.POST.get('category')
        if category_id:
            blog.category_id = category_id

        if 'image' in request.FILES:
            blog.image = request.FILES['image']

        blog.save()
        messages.success(request, 'Blog updated successfully!')
        return redirect('user_blog')

    context = {
        'blog': blog,
        'categories': categories,
        'is_edit': True,
        'tags_json': mark_safe(json.dumps(tags)),  # ✅ safe JSON
    }
    return render(request, 'blog/edit_blog.html', context)

@login_required
def delete_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug, author=request.user.profile)

    if request.method == 'POST':
        blog.delete()
        messages.success(request, 'Blog deleted successfully!')
        return redirect('user_blog')

    return render(request, 'blog/confirm_delete.html', {'blog': blog})

@login_required
def view_user_profile(request, username):
    user_obj = get_object_or_404(User, username=username)
    profile = get_object_or_404(user_obj.profile.__class__, user=user_obj)

    # Visibility checks
    if request.user != user_obj:
        if profile.profile_visibility == 'private':
            return render(request, 'blog/private_profile.html', {'profile': profile})
        if profile.profile_visibility == 'followers':
            is_follower = Follow.objects.filter(follower=request.user, following=user_obj, is_approved=True).exists()
            if not is_follower:
                return render(request, 'blog/followers_only_profile.html', {'profile': profile})
    else:
        is_follower = True

    # Fetch blogs
    blogs = Blog.objects.filter(author=profile, is_published=True).order_by('-created_at')

    # Check if request.user is following this profile
    is_following = Follow.objects.filter(follower=request.user, following=user_obj, is_approved=True).exists()

    # Calculate followers/following counts
    followers_count = Follow.objects.filter(following=user_obj, is_approved=True).count()
    following_count = Follow.objects.filter(follower=user_obj, is_approved=True).count()

    return render(request, 'blog/profile_view.html', {
        'profile': profile,
        'blogs': blogs,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
    })

@login_required
def my_blogs(request):
    user_profile = request.user.profile

    blogs = (
        Blog.objects.filter(author=user_profile, is_published=True)
        .select_related('author', 'category')
        .prefetch_related('tags')
        .annotate(
            num_likes=Count('likes', distinct=True),
            num_comments=Count('comments', distinct=True),
            num_views=Count('views', distinct=True)
        )
        .order_by('-created_at')
    )

    # Compute stats directly from DB fields
    total_blogs = blogs.count()
    total_likes = blogs.aggregate(total_likes=Sum('likes'))['total_likes'] or 0  # safe fallback
    total_views = blogs.aggregate(total_views=Sum('views'))['total_views'] or 0

    # Since we annotated likes/comments, adjust aggregation properly
    total_likes = sum(blog.num_likes for blog in blogs)
    total_comments = sum(blog.num_comments for blog in blogs)
    total_views = sum(blog.num_views for blog in blogs)

    context = {
        'blogs': blogs,
        'categories': Category.objects.all(),
        'total_blogs': total_blogs,
        'total_likes': total_likes,
        'total_views': total_views,
        'total_comments': total_comments,
    }

    return render(request, 'blog/my_blog.html', context)

@require_POST
@login_required
def toggle_like(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    like, created = Like.objects.get_or_create(user=request.user, blog=blog)

    if not created:
        # Already liked → remove it
        like.delete()
        liked = False
    else:
        liked = True
        if blog.author.user != request.user:
            Notification.objects.create(
                recipient=blog.author.user,
                sender=request.user,
                blog=blog,
                notification_type='like'
            )

    return JsonResponse({
        'liked': liked,
        'like_count': blog.likes.count(),
    })

@login_required
def add_comment(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id')

    if not content:
        return JsonResponse({'success': False, 'error': 'Empty comment'}, status=400)

    parent = Comment.objects.filter(id=parent_id).first() if parent_id else None
    comment = Comment.objects.create(
        blog=blog,
        user=request.user,
        content=content,
        parent=parent
    )

    # Render just one comment block (no recursion)
    html = render_to_string('blog/comment_single.html', {'comment': comment}, request=request)
    return JsonResponse({'success': True, 'html': html, 'parent_id': parent_id})


@login_required
def load_comments(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    comments = blog.comments.filter(is_approved=True, parent__isnull=True)
    return render(request, 'blog/comments.html', {'comments': comments})


@login_required
def trending(request):
    filter_option = request.GET.get('filter', 'all')
    search_query = request.GET.get('q', '')

    blogs = Blog.objects.all().order_by('-views', '-created_at')

    # Apply existing date filters
    if filter_option == 'today':
        blogs = blogs.filter(created_at__date=date.today())
    elif filter_option == 'week':
        week_ago = timezone.now() - timedelta(days=7)
        blogs = blogs.filter(created_at__gte=week_ago)
    elif filter_option == 'month':
        month_ago = timezone.now() - timedelta(days=30)
        blogs = blogs.filter(created_at__gte=month_ago)

    # Apply search filter
    if search_query:
        blogs = blogs.filter(title__icontains=search_query)

    # --- Trending logic ---
    trending_blogs = blogs[:3]  # Top 3 blogs

    for blog in trending_blogs:
        author_user = blog.author.user
        # Check if the notification already exists to avoid spamming
        already_notified = Notification.objects.filter(
            recipient=author_user,
            notification_type='trending',
            blog=blog
        ).exists()

        if not already_notified:
            Notification.objects.create(
                recipient=author_user,
                sender=None,  # System-generated
                notification_type='trending',
                blog=blog,
                message=f"Your blog '{blog.title}' is now trending in the top 3!"
            )

    # --- Visibility filtering (your original logic) ---
    visible_blogs = []
    for blog_post in blogs.select_related('author', 'author__user').prefetch_related('tags'):
        profile = blog_post.author
        user_obj = profile.user

        if profile.profile_visibility == 'public':
            visible_blogs.append(blog_post)
        elif profile.profile_visibility == 'followers':
            if request.user.is_authenticated and (
                request.user.id == profile.user.id or 
                Follow.objects.filter(follower=request.user, following=profile.user, is_approved=True).exists()
            ):
                visible_blogs.append(blog_post)
        elif profile.profile_visibility == 'private':
            if request.user.is_authenticated and request.user.id == profile.user.id:
                visible_blogs.append(blog_post)

    context = {'blogs': visible_blogs}
    return render(request, 'blog/trending_blogs.html', context)


@login_required
def setting(request):
    profile = request.user.profile
    return render(request, 'blog/setting_page.html', {'profile': profile})

@login_required
def update_settings(request):
    profile = request.user.profile
    if request.method == 'POST':
        visibility = request.POST.get('profile_visibility')
        if visibility in ['public', 'followers', 'private']:
            profile.profile_visibility = visibility
            profile.save()
    return redirect('setting')

@login_required
def change_password(request):
    """
    Handles password change using Django's built-in PasswordChangeForm.
    Keeps the user logged in after a successful password update.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps session active
            messages.success(request, "Your password has been changed successfully!")
            return redirect('setting')  # back to settings page
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'blog/change_password.html', {'form': form})

@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect('login')  # redirect to login page after logout confirmation

    # If it's a GET request, render a confirmation page
    return render(request, 'blog/logout.html')

@login_required
def email_settings(request):
    """Displays primary + additional emails."""
    additional_emails = UserEmail.objects.filter(user=request.user)
    return render(request, 'blog/email_setting.html', {'additional_emails': additional_emails})


@login_required
def add_email(request):
    """Adds a new email for the user and sends an OTP for verification."""
    if request.method == 'POST':
        email = request.POST.get('email')

        if email:
            if email == request.user.email or UserEmail.objects.filter(email=email).exists():
                messages.error(request, "This email is already in use.")
            else:
                # Create unverified record first
                ue = UserEmail.objects.create(user=request.user, email=email, verified=False)
                try:
                    # Send OTP email (defined in utils.py)
                    create_and_send_otp(request.user, email)
                    messages.success(request, f"Verification code sent to {email}. Please verify it.")
                    return redirect('email_verify')  # page where user enters OTP
                except Exception:
                    ue.delete()  # rollback if sending fails
                    messages.error(request, "Failed to send verification email. Please try again later.")
        else:
            messages.error(request, "Invalid email address.")

    return redirect('email_settings')


@login_required
def delete_email(request, email_id):
    """Removes a user-added email."""
    email_obj = get_object_or_404(UserEmail, id=email_id, user=request.user)
    email_obj.delete()
    messages.success(request, "Email deleted successfully.")
    return redirect('email_settings')


@login_required
def set_primary_email(request, email_id):
    """Sets a user-added email as the new primary email."""
    email_obj = get_object_or_404(UserEmail, id=email_id, user=request.user)
    if not email_obj.verified:
        messages.error(request, "You can only set verified emails as primary.")
    else:
        request.user.email = email_obj.email
        request.user.save()
        messages.success(request, f"{email_obj.email} set as your primary email.")
    return redirect('email_settings')

@login_required
@require_POST
def send_email_otp(request, email_id=None):
    """
    Send OTP to an existing UserEmail or to an address posted in form.
    If email_id is provided, send to that UserEmail.email (used for resend).
    """
    # Determine target email
    if email_id:
        email_obj = get_object_or_404(UserEmail, id=email_id, user=request.user)
        target_email = email_obj.email
    else:
        target_email = request.POST.get('email')
        if not target_email:
            messages.error(request, "No email provided.")
            return redirect('email_settings')

    # Rate limit: allow only a small number of outstanding OTPs per email/user
    recent_otps = EmailOTP.objects.filter(user=request.user, email=target_email, created_at__gte=timezone.now()-timezone.timedelta(minutes=15))
    if recent_otps.count() >= 3:
        messages.error(request, "Too many OTP requests. Try again later.")
        return redirect('email_settings')

    # Create and send
    try:
        otp_obj = create_and_send_otp(request.user, target_email)
        messages.success(request, f"OTP sent to {target_email}. Check your email.")
    except Exception as e:
        messages.error(request, "Failed to send email. Check server settings.")
    return redirect('email_verify')  # show OTP entry page


@login_required
def email_verify_page(request):
    """
    Renders OTP entry page — user inputs email and code.
    """
    return render(request, 'blog/email_verify.html')  # we'll add template below


@login_required
@require_POST
def verify_email_otp(request):
    """
    Verify posted OTP and mark UserEmail as verified (or set user.email if primary).
    Expect POST parameters: email, code
    """
    email = request.POST.get('email')
    code = request.POST.get('code')
    if not email or not code:
        messages.error(request, "Email and code are required.")
        return redirect('email_verify')

    # Find latest active OTP for that email & user
    otp_qs = EmailOTP.objects.filter(user=request.user, email=email, verified=False).order_by('-created_at')
    if not otp_qs.exists():
        messages.error(request, "No OTP found for this email. Request a new code.")
        return redirect('email_verify')

    otp_obj = otp_qs.first()
    ok, reason = otp_obj.verify_code(code)
    otp_obj.save()  # persists attempts/verified
    if ok:
        # mark or create UserEmail and set verified
        ue, created = UserEmail.objects.get_or_create(user=request.user, email=email)
        ue.verified = True
        ue.save()
        messages.success(request, f"{email} verified successfully.")
        return redirect('email_settings')
    else:
        if reason == 'expired':
            messages.error(request, "OTP expired. Request a new one.")
        elif reason == 'max_attempts_exceeded':
            messages.error(request, "Too many attempts. Request a new code.")
        else:
            messages.error(request, "Invalid code. Try again.")
        return redirect('email_verify')
    
@login_required
def resend_verification(request, email):
    try:
        create_and_send_otp(request.user, email)
        messages.success(request, f"Verification code resent to {email}.")
    except Exception:
        messages.error(request, "Failed to resend verification email.")
    return redirect('email_settings')

@login_required
def try_another_way(request):
    if request.method == "POST":
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            otp = random.randint(100000, 999999)  # 6-digit OTP
            request.session['reset_otp'] = otp
            request.session['reset_user'] = user.username

            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {otp}',
                'noreply@yourdomain.com',
                [user.email],
                fail_silently=False,
            )
            messages.success(request, f'OTP has been sent to {user.email}')
            return redirect('verify_otp')

        except User.DoesNotExist:
            messages.error(request, 'User with this username does not exist.')
            return redirect('try_another_way')  # <--- Important, else POST with invalid username returns None

    # This handles GET request
    return render(request, 'blog/try_another_way.html')

@login_required
def verify_otp(request):
    if request.method == "POST":
        otp_input = request.POST.get('otp')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        session_otp = str(request.session.get('reset_otp'))
        username = request.session.get('reset_user')

        if not username or not session_otp:
            messages.error(request, "Session expired. Please try again.")
            return redirect('try_another_way')

        if otp_input != session_otp:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('verify_otp')

        if new_password1 != new_password2:
            messages.error(request, "Passwords do not match.")
            return redirect('verify_otp')

        try:
            user = User.objects.get(username=username)
            user.password = make_password(new_password1)
            user.save()

            # Clear session
            del request.session['reset_otp']
            del request.session['reset_user']

            messages.success(request, "Password reset successful. You can now log in with your new password.")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect('try_another_way')

    return render(request, 'blog/verify_otp.html')


@login_required
def search_users(request):
    query = request.GET.get('q', '').strip()
    users = User.objects.exclude(id=request.user.id).select_related('profile')

    if query:
        users = users.filter(
            Q(username__icontains=query) | Q(profile__name__icontains=query)
        )

    return render(request, 'blog/search_users.html', {'users': users, 'query': query})

@login_required
def send_follow_request(request, username):
    target_user = get_object_or_404(User, username=username)

    if request.user == target_user:
        messages.warning(request, "You can't follow yourself, bro!")
        return redirect('view_user_profile', username=username)

    # Check if already following or requested
    existing = Follow.objects.filter(follower=request.user, following=target_user).first()
    if existing:
        if not existing.is_approved:
            messages.info(request, f"Follow request to {username} is already pending.")
        else:
            messages.info(request, f"You already follow {username}.")
        return redirect('view_user_profile', username=username)

    # ✅ Get visibility from Profile model
    visibility = target_user.profile.profile_visibility

    if visibility in ['private', 'followers']:
        follow = Follow.objects.create(
            follower=request.user,
            following=target_user,
            is_approved=False
        )
        Notification.objects.create(
            recipient=target_user,
            sender=request.user,
            follow=follow,
            notification_type='follow_request',
            message=f"{request.user.username} sent you a follow request."
        )
        messages.success(request, f"Follow request sent to {username}.")
    else:
        follow = Follow.objects.create(
            follower=request.user,
            following=target_user,
            is_approved=True
        )
        Notification.objects.create(
            recipient=target_user,
            sender=request.user,
            follow=follow,
            notification_type='follow',
            message=f"{request.user.username} started following you."
        )
        messages.success(request, f"You are now following {username}.")

    return redirect('view_user_profile', username=username)


@login_required
def approve_follow_request(request, follower_username):
    follower_user = get_object_or_404(User, username=follower_username)
    follow_obj = get_object_or_404(
        Follow, follower=follower_user, following=request.user, is_approved=False
    )
    follow_obj.is_approved = True
    follow_obj.save()

    messages.success(request, f"You approved {follower_user.username}'s follow request.")
    return redirect('follow_requests')


@login_required
def reject_follow_request(request, follower_username):
    follower_user = get_object_or_404(User, username=follower_username)
    follow_obj = get_object_or_404(
        Follow, follower=follower_user, following=request.user, is_approved=False
    )
    follow_obj.delete()

    messages.info(request, f"You rejected {follower_user.username}'s follow request.")
    return redirect('follow_requests')

@login_required
def follow_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    if request.user == target_user:
        return JsonResponse({"message": "You can’t follow yourself."}, status=400)

    existing = Follow.objects.filter(follower=request.user, following=target_user).first()
    if existing:
        if existing.is_approved:
            existing.delete()
            return JsonResponse({"status": "unfollowed", "message": f"You unfollowed {target_user.username}."})
        else:
            return JsonResponse({"message": f"Follow request to {target_user.username} is pending."}, status=200)

    visibility = target_user.profile.profile_visibility
    if visibility == 'private':
        Follow.objects.create(follower=request.user, following=target_user, is_approved=False)
        return JsonResponse({"status": "requested", "message": f"Follow request sent to {target_user.username}."})
    else:
        Follow.objects.create(follower=request.user, following=target_user, is_approved=True)
        return JsonResponse({"status": "followed", "message": f"You are now following {target_user.username}."})


@login_required
def unfollow_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    follow_relation = Follow.objects.filter(follower=request.user, following=target_user).first()
    if not follow_relation:
        messages.warning(request, f"You are not following {target_user.username}.")
    else:
        follow_relation.delete()
        messages.success(request, f"You unfollowed {target_user.username}.")

    return redirect('view_user_profile', username=target_user.username)

@login_required
def toggle_follow_ajax(request, username):
    if request.method != "POST":
        return JsonResponse({"message": "POST only"}, status=405)

    target = get_object_or_404(User, username=username)
    if request.user == target:
        return JsonResponse({"message": "You can’t follow yourself."}, status=400)

    relation = Follow.objects.filter(follower=request.user, following=target).first()

    if relation and relation.is_approved:
        relation.delete()
        return JsonResponse({"status": "unfollowed"})
    if relation and not relation.is_approved:
        return JsonResponse({"status": "requested"})

    vis = getattr(target.profile, "profile_visibility", "public")
    if vis == "private":
        follow = Follow.objects.create(follower=request.user, following=target, is_approved=False)
        Notification.objects.create(
            recipient=target,
            sender=request.user,
            follow=follow,
            notification_type='follow_request'
        )
        return JsonResponse({"status": "requested"})
    else:
        Follow.objects.create(follower=request.user, following=target, is_approved=True)
        Notification.objects.create(
            recipient=target,
            sender=request.user,
            notification_type='follow'
        )
    return JsonResponse({"status": "followed"})


@login_required
def notification_panel(request):
    notifications = Notification.objects.filter(recipient=request.user)\
                        .select_related('sender', 'blog', 'comment', 'follow')\
                        .order_by('-created_at')
    return render(request, 'blog/notifications.html', {'notifications': notifications})


@login_required
@require_POST
def mark_all_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"success": True})


@login_required
@require_POST
def clear_all_notifications(request):
    Notification.objects.filter(recipient=request.user).delete()
    return JsonResponse({"success": True})


@login_required
@require_POST
def handle_follow_request(request, notif_id, action):
    notif = get_object_or_404(Notification, id=notif_id, recipient=request.user, notification_type='follow_request')
    follow_obj = notif.follow

    if action not in ['approve', 'reject']:
        return JsonResponse({"error": "Invalid action"}, status=400)

    if not follow_obj:
        return JsonResponse({"error": "Follow request not found"}, status=404)

    if action == 'approve':
        follow_obj.is_approved = True
        follow_obj.save()   

        # Update notification for current user (the one accepting)
        notif.message = f"You accepted {follow_obj.follower.username}'s follow request."
        notif.is_read = True
        notif.save()

        # Notification for the follower (who sent the request)
        Notification.objects.create(
            recipient=follow_obj.follower,
            sender=request.user,
            notification_type='follow_request',
            message=f"{request.user.username} accepted your follow request."
        )

        return JsonResponse({
            "status": "approved",
            "notif_id": notif.id,
            "new_message": notif.message
        })

    elif action == 'reject':
        # Save follower info before deleting
        follower_user = follow_obj.follower
        follow_obj.delete()

        # Update notification for current user
        notif.message = f"You rejected {follower_user.username}'s follow request."
        notif.is_read = True
        notif.save()

        # Notify the follower about rejection
        Notification.objects.create(
            recipient=follower_user,
            sender=request.user,
            notification_type='follow_request',
            message=f"{request.user.username} rejected your follow request."
        )

        return JsonResponse({
            "status": "rejected",
            "notif_id": notif.id,
            "new_message": notif.message
    })


    
@login_required
def notifications_view(request):
    # Get notifications for the logged-in user, newest first
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'blog/blogs.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })

@login_required
def get_follow_counts(request, username=None):
    """
    Returns followers and following counts as JSON.
    If username is None, return counts for the logged-in user.
    """
    if username:
        user_obj = get_object_or_404(User, username=username)
    else:
        user_obj = request.user

    followers_count = Follow.objects.filter(following=user_obj, is_approved=True).count()
    following_count = Follow.objects.filter(follower=user_obj, is_approved=True).count()

    return JsonResponse({
        'followers_count': followers_count,
        'following_count': following_count
    })

@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirmation = request.POST.get('confirmation')

        if not request.user.check_password(password):
            messages.error(request, "Incorrect password.")
            return redirect('delete_account')

        if confirmation != "DELETE":
            messages.error(request, 'You must type "DELETE" to confirm.')
            return redirect('delete_account')

        user = request.user

        # Delete all user-related data
        Blog.objects.filter(author=user.profile).delete()          # delete blogs
        Comment.objects.filter(user=user).delete()                 # delete comments
        Like.objects.filter(user=user).delete()                    # delete likes
        Follow.objects.filter(follower=user).delete()              # delete following
        Follow.objects.filter(following=user).delete()             # delete followers

        # Optionally, delete notifications
        user.notifications.all().delete()  # if you have a related_name on Notification model

        # Finally, delete the user
        user.delete()

        # Logout the user
        logout(request)
        messages.success(request, "Your account and all associated data have been permanently deleted.")
        return redirect('login')  # or login page

    return render(request, 'blog/delete_account.html')