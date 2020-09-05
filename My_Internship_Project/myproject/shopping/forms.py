from django import forms
class Signup1 ( forms.Form ):
    FirstName = forms.CharField ( max_length = 100 )
    Email = forms.EmailField ( )
    Password = forms.CharField ( max_length = 40 , widget = forms.PasswordInput )
    Cpassword = forms.CharField ( max_length = 40 , widget = forms.PasswordInput )


class Verify ( forms.Form ):
    otp1 = forms.IntegerField ( )


class Loginx ( forms.Form ):
    Email = forms.EmailField ( )
    Password = forms.CharField (max_length = 40)