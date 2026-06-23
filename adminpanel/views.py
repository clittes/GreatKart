
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from accounts.models import Account
from django.contrib import messages,auth
from django.views.decorators.cache import cache_control

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def admin_dashboard(request):
    if not request.user.is_admin:
        return redirect('home')
    users = Account.objects.all().order_by('-date_joined')
    paginator = Paginator(users, 5) # get current page number
    page = request.GET.get('page') 
    # get users for current page 
    paged_users = paginator.get_page(page)
    context = {
        'users': paged_users,
    }
    return render( request, 'adminpanel/dashboard.html', context)

@login_required(login_url='login')
def block_user(request, user_id):
    user = Account.objects.get(id=user_id)
    user.is_active = False
    user.save()
    return redirect('admin_dashboard')


@login_required(login_url='login')
def unblock_user(request, user_id):
    user = Account.objects.get(id=user_id)
    user.is_active = True
    user.save()
    return redirect('admin_dashboard')

def search_users(request):
    keyword = request.GET.get('keyword')
    users = Account.objects.filter(Q(first_name__icontains=keyword) | Q(email__icontains=keyword) | Q(phone_number__icontains=keyword))
    context = { 
        'users': users,
        'keyword': keyword,
             } 
    return render( request, 'adminpanel/dashboard.html', context )

@login_required(login_url = 'login')
def logout_user(request):
    auth.logout(request)
    messages.success(request,"You are logged out")
    return redirect('login')
