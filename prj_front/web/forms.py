from allauth.account.forms import SignupForm


class CustomSignupFormDif(SignupForm):
    def save(self, request):
        from allauth.account.forms import SignupForm
        user = super(CustomSignupFormDif, self).save(request)
        return user
