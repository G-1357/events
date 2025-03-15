from allauth.account.forms import SignupForm

class CustomSignupFormDif(SignupForm):
    def save(self, request):
        user = super(CustomSignupFormDif, self).save(request)
        return user