
from django.http import HttpResponse
from django.shortcuts import redirect, render,get_object_or_404

from .forms import RegistrationForm,UserForm,UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.cache import never_cache




# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage



# Create your views here.

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            phone_number = form.cleaned_data.get('phone_number')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            username = email.split("@")[0] 


            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username,password=password)
            user.phone_number = phone_number
            user.save()
            
            # USER ACTIVATION
            current_site =  get_current_site(request)
            mail_subject = 'Please Activate Your Account'
            message = render_to_string('accounts/account_verification_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request,'Thank you for registering with us,we have sent an verification email to your email address.Please verify it. ')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    
    context ={
        'form' : form,
    }
    return render(request,'accounts/register.html',context)

@never_cache
def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        

        user = auth.authenticate(request, username=email,password=password)
        if user is not None:
            auth.login(request,user)
            messages.success(request,'You Are Now Logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Inavalid login credentials')
            return redirect('login')
    return render(request,'accounts/login.html')

@never_cache
@login_required(login_url ="login")
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')

def activate(request,uidb64, token):
    try:
        uid    = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(id=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user =None
        
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulations Your account is activated.')
        return redirect('login')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register')
    
@login_required(login_url ="login")
def dashboard(request):
    return render(request,'accounts/dashboard.html')

def forgotPassword(request):
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            
            # Reset password email
            current_site =  get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            
            messages.success(request,'Password reset email has been sent to your email address.')
            return redirect('login')        
        else:
            messages.error(request,'Account does not exist!')
            return redirect('forgotPassword')
    return render(request,'accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(id=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user =None
        
        
    if user is not None and default_token_generator.check_token(user,token):
         request.session['uid']=uid
         messages.success(request,'Please reset your password')
         return redirect('resetPassword')
    else:
        messages.error(request,'This link has been expired')
        return redirect('login')
    
def resetPassword(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset succesfull')
            return redirect('login')
            
        else:
            messages.error(request,'Password does not match!')
            return redirect('resetPassword')
    else:
        return render(request,'accounts/resetPassword.html')
    
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile,user = request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST,instance=request.user)
        profile_form = UserProfileForm(request.POST,request.FILES,instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'Your Profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form':user_form,
        'profile_form':profile_form,
        'userprofile':userprofile,
    }
    return render(request,'accounts/edit_profile.html',context)