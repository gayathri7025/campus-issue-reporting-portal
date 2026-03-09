from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import logout
from django.db.models import Q  # Required for Search
from .models import Issue
from .forms import IssueForm, RegisterForm

# 1. Home Page
def home(request):
    return render(request, 'core/home.html')

# 2. Dashboard (Requires Login) - Updated with Search & Filters
@login_required
def dashboard(request):
    # 1. Get Base Query (Admin sees all, Student sees own)
    if request.user.is_staff:
        all_issues = Issue.objects.all()
    else:
        all_issues = Issue.objects.filter(reported_by=request.user)

    # 2. Get Filter Values from URL (GET parameters)
    query = request.GET.get('q')
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')

    # 3. Apply Filters
    if query:
        all_issues = all_issues.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if status_filter:
        all_issues = all_issues.filter(status=status_filter)

    if category_filter:
        all_issues = all_issues.filter(category=category_filter)

    # Order results
    all_issues = all_issues.order_by('-created_at')

    # 4. Calculate Counts (Based on the FILTERED results)
    total = all_issues.count()
    pending = all_issues.filter(status='Pending').count()
    resolved = all_issues.filter(status='Resolved').count()
    in_progress = all_issues.filter(status='In Progress').count()

    context = {
        'issues': all_issues,
        'total': total,
        'pending': pending,
        'resolved': resolved,
        'in_progress': in_progress
    }
    return render(request, 'core/dashboard.html', context)

# 3. Create New Issue + Send Email
@login_required
def create_issue(request):
    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.reported_by = request.user
            issue.save()

            # 📧 SEND EMAIL TO ADMIN
            subject = f"New Campus Issue: {issue.title}"
            message = f"A new issue has been reported by {request.user.username}.\n\nTitle: {issue.title}\nLocation: {issue.location}\nDescription: {issue.description}\n\nPlease check the dashboard."
            recipient_list = ['admin@campus.edu']

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=True,
            )

            return redirect('dashboard')
    else:
        form = IssueForm()
    return render(request, 'core/create_issue.html', {'form': form})

# 4. Update Status + Send Confirmation
@login_required
def update_status(request, issue_id):
    if request.user.is_staff:
        issue = get_object_or_404(Issue, id=issue_id)
        new_status = request.POST.get('status')
        admin_comment = request.POST.get('admin_comment')

        status_changed = (new_status and new_status != issue.status)

        if status_changed or admin_comment:
            if status_changed:
                old_status = issue.status
                issue.status = new_status

            if admin_comment:
                issue.admin_comment = admin_comment

            issue.save()

            if status_changed:
                subject = f"Update on your Issue: {issue.title}"
                message_body = f"Hello {issue.reported_by.username},\n\nThe status of your issue '{issue.title}' has been updated.\n\nOld Status: {old_status}\nNew Status: {new_status}"
                if admin_comment:
                    message_body += f"\n\nAdmin Note: {admin_comment}"
                message_body += "\n\nThank you for reporting."

                send_mail(
                    subject,
                    message_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [issue.reported_by.email],
                    fail_silently=True,
                )

    return redirect('dashboard')

# 5. Delete Issue (Admin Only)
@login_required
def delete_issue(request, issue_id):
    if request.user.is_staff:
        issue = get_object_or_404(Issue, id=issue_id)
        issue.delete()
    return redirect('dashboard')

# 6. Custom Logout
def custom_logout(request):
    logout(request)
    return redirect('login')

# 7. Register
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})