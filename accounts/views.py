


from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from .forms import RegistrationForm,UserForm,UserProfileForm,ChangePasswordForm
from . models import Account, UserProfile
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required

# verifiaction email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import  urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.views.decorators.cache import cache_control



def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():         
            first_name      = form.cleaned_data['first_name']
            last_name       = form.cleaned_data['last_name']
            phone_number    = form.cleaned_data['phone_number']
            email           = form.cleaned_data['email']
            password        = form.cleaned_data['password']
            username        = email.split("@")[0]
            user = Account.objects.create_user(first_name = first_name,last_name = last_name,email=email,username=username,password=password)
            user.phone_number = phone_number
            user.is_active = False
            user.save()
            # user activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message      = render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            return redirect('/accounts/login/?command=verification&email='+email)
            
    else :

        form = RegistrationForm()
    context = {
        'form':form,
    }
    return render(request,'accounts/register.html',context)

def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            messages.error(request,'Invalid login credentials')
            return redirect('login')
        if not user.is_active: 
            messages.error( request,'Please activate your account first.')
            return redirect('login')

        user = auth.authenticate(request,email=email,password=password)

        if user is not None:
            auth.login(request, user)
            if user.is_admin:
                messages.success(request,'Welcome Admin')
                return redirect('admin_dashboard')
            else:
                messages.success( request, 'You are logged in')
                return redirect('home')
        else:
            messages.error( request, 'Invalid login credentials' )
            return redirect('login')
    return render(request,'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,"You are logged out")
    return redirect('login')

def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulations! Your account is activated')
        return redirect('login')
    else:
        messages.error(request,'Invaid activation links')
        return redirect('register')
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login')
def dashboard(request):
    # Get or create the user profile for the logged-in user
    userprofile, created= UserProfile.objects.get_or_create(user=request.user)

    context = {
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            # reset passwword email
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message      = render_to_string('accounts/reset_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,'Password reset email send to your email address')
            return redirect('login')
        
        else:
            messages.error(request,'Account does not exixt')
            return redirect('forgotPassword')
    return render(request,'accounts/forgotPassword.html')

def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid);
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
          user = None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request,'This link has been expired')
        return redirect('login')
    
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset success')
            return redirect('login')

        else:
            messages.error(request,'Password do not match')
            return redirect('resetPassword')
    else:
        return render(request,'accounts/resetPassword.html')
    



@login_required(login_url='login')
def edit_profile(request):

    userprofile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        old_email = request.user.email
        user_form = UserForm(request.POST,instance=request.user)
        profile_form = UserProfileForm(request.POST,request.FILES,instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            new_email = user_form.cleaned_data['email']

            # EMAIL CHANGED
            if old_email != new_email:
                # CHECK EMAIL EXISTS
                if Account.objects.filter(email=new_email).exclude(id=request.user.id).exists():
                    messages.error(request,'Email already exists')
                    return redirect('edit_profile')
                # SAVE TEMP EMAIL IN SESSION
                request.session['new_email'] = new_email
                # SAVE OTHER PROFILE DATA
                profile_form.save()

                request.user.first_name = user_form.cleaned_data['first_name']
                request.user.last_name = user_form.cleaned_data['last_name']
                request.user.phone_number = user_form.cleaned_data['phone_number']
                request.user.save()

                # SEND EMAIL VERIFICATION
                current_site = get_current_site(request)

                mail_subject = 'Verify your new email'

                message = render_to_string(
                    'accounts/change_email_verification.html',
                    {
                        'user': request.user,
                        'domain': current_site,
                        'uid': urlsafe_base64_encode(
                            force_bytes(request.user.pk)
                        ),
                        'token': default_token_generator.make_token(
                            request.user
                        ),
                    }
                )

                send_email = EmailMessage(mail_subject, message, to=[new_email])

                send_email.send()

                messages.success(request,'Verification email sent to your new email address')

                return redirect('edit_profile')

            else:
                user_form.save()
                profile_form.save()
                messages.success(request,'Profile updated successfully')
                return redirect('edit_profile')

    else:

        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {

        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }

    return render(request,'accounts/edit_profile.html',context)

from django.utils.http import urlsafe_base64_decode


@login_required(login_url='login')
def verify_new_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except:
        user = None

    if user is not None and default_token_generator.check_token(user, token):

        new_email = request.session.get('new_email')
        if new_email:
            user.email = new_email
            user.save()
            del request.session['new_email']
            messages.success(request,'Email updated successfully')
            return redirect('edit_profile')

    messages.error(request,'Invalid or expired verification link')

    return redirect('edit_profile')



@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']
            user = Account.objects.get( username__exact=request.user.username)
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success( request, 'Password updated successfully.')
                return redirect('login')
            else:
                messages.error(request,
                    'Please enter valid current password.')
                return redirect('change_password')
    else:
        form = ChangePasswordForm()

    context = {
        'form': form,
    }
    return render(request,'accounts/change_password.html',context)


@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,"You are logged out")
    return redirect('login')


    


    
        