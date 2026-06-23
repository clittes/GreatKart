from django import forms
from . models import Account,UserProfile
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import Account
import re


class RegistrationForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter Password',
            'class': 'form-control',
        })
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'class': 'form-control',
        })
    )

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if len(first_name) < 3:
            raise ValidationError("First name must contain at least 3 characters.")

        if not first_name.isalpha():
            raise ValidationError("First name should contain only alphabets.")

        return first_name

  
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        if len(last_name) < 1:
            raise ValidationError("Last name is required.")

        if not last_name.isalpha():
            raise ValidationError("Last name should contain only alphabets.")

        return last_name

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Check existing email
        if Account.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")

        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        # Only digits allowed
        if not phone_number.isdigit():
            raise ValidationError("Phone number must contain only digits.")

        # Indian phone validation
        if len(phone_number) != 10:
            raise ValidationError("Phone number must be 10 digits.")

        if not phone_number.startswith(('6', '7', '8', '9')):
            raise ValidationError("Enter a valid Indian phone number.")

        return phone_number

    def clean_password(self):
        password = self.cleaned_data.get('password')

        # Minimum length
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters.")

        # At least one uppercase
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter.")

        # At least one lowercase
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter.")

        # At least one digit
        if not re.search(r'[0-9]', password):
            raise ValidationError("Password must contain at least one number.")

        # At least one special character
        if not re.search(r'[@$!%*#?&]', password):
            raise ValidationError(
                "Password must contain at least one special character."
            )

        return password

    # ---------------- CONFIRM PASSWORD ----------------
    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError(
                    "Password and Confirm Password do not match."
                )

        return cleaned_data
    
    
class UserForm(forms.ModelForm):

    class Meta:

        model = Account

        fields = (
            'first_name',
            'last_name',
            'email',
            'phone_number',
        )

    def __init__(self, *args, **kwargs):

        super(UserForm, self).__init__(*args, **kwargs)

        for field in self.fields:

            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_first_name(self):

        first_name = self.cleaned_data.get('first_name')

        if len(first_name) < 3:

            raise ValidationError(
                "First name must contain at least 3 characters."
            )

        if not first_name.isalpha():

            raise ValidationError(
                "First name should contain only alphabets."
            )

        return first_name

    def clean_last_name(self):

        last_name = self.cleaned_data.get('last_name')

        if not last_name.isalpha():

            raise ValidationError(
                "Last name should contain only alphabets."
            )

        return last_name

    def clean_email(self):

        email = self.cleaned_data.get('email')

        user = self.instance

        # exclude current user email
        if Account.objects.filter(email=email)\
            .exclude(id=user.id).exists():

            raise ValidationError(
                "Email already exists."
            )

        return email

    def clean_phone_number(self):

        phone_number = self.cleaned_data.get('phone_number')

        if not phone_number.isdigit():

            raise ValidationError(
                "Phone number must contain only digits."
            )

        if len(phone_number) != 10:

            raise ValidationError(
                "Phone number must be 10 digits."
            )

        return phone_number
class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False,error_messages={'invalid':("image files only")},widget=forms.FileInput)
    class Meta:
        model= UserProfile
        fields = ('address_line1','address_line2','city','state','country','profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    def clean_address_line1(self):
        address = self.cleaned_data.get('address_line1')

        if len(address) < 5:
            raise ValidationError(
                "Address Line 1 must contain at least 5 characters."
            )

        if address.isdigit():
            raise ValidationError(
                "Address cannot contain only numbers."
            )

        return address

    # ADDRESS LINE 2 VALIDATION
    def clean_address_line2(self):
        address = self.cleaned_data.get('address_line2')

        # Optional field check
        if address:

            if len(address) < 3:
                raise ValidationError(
                    "Address Line 2 is too short."
                )

            if address.isdigit():
                raise ValidationError(
                    "Address cannot contain only numbers."
                )

        return address

  
    def clean_city(self):
        city = self.cleaned_data.get('city')

        if city.isdigit():
            raise ValidationError(
                "City name cannot contain only numbers."
            )

        return city

  
    def clean_state(self):
        state = self.cleaned_data.get('state')

        if state.isdigit():
            raise ValidationError(
                "State name cannot contain only numbers."
            )

        return state

  
    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')

        if picture:

            # File size validation
            if picture.size > 2 * 1024 * 1024:
                raise ValidationError(
                    "Image size should be less than 2MB."
                )

            valid_extensions = ['.jpg', '.jpeg', '.png']

            import os
            ext = os.path.splitext(picture.name)[1].lower()

            if ext not in valid_extensions:
                raise ValidationError(
                    "Only JPG, JPEG, and PNG files are allowed."
                )

        return picture
    

class ChangePasswordForm(forms.Form):

    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter Current Password',
            'class': 'form-control',
        })
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter New Password',
            'class': 'form-control',
        })
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm New Password',
            'class': 'form-control',
        })
    )

    # NEW PASSWORD VALIDATION
    def clean_new_password(self):

        password = self.cleaned_data.get('new_password')

        # Minimum length
        if len(password) < 8:
            raise ValidationError(
                "Password must be at least 8 characters."
            )

        # Uppercase check
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                "Password must contain at least one uppercase letter."
            )

        # Lowercase check
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                "Password must contain at least one lowercase letter."
            )

        # Number check
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                "Password must contain at least one number."
            )

        # Special character check
        if not re.search(r'[@$!%*#?&]', password):
            raise ValidationError(
                "Password must contain at least one special character."
            )

        return password

    # CONFIRM PASSWORD VALIDATION
    def clean(self):

        cleaned_data = super().clean()

        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password:

            if new_password != confirm_password:
                raise ValidationError(
                    "New Password and Confirm Password do not match."
                )

        return cleaned_data