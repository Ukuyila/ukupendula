from django import forms
from uuid import uuid4
# crispy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field

# Local imports
from .models import *


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
                    required=True,
                    label='First Name',
                    widget=forms.TextInput(
                        attrs={'class': 'form-control mb-3',
                               'placeholder': 'Enter first name',
                               })
                    )
    last_name = forms.CharField(
                    required=True,
                    label='Last Name',
                    widget=forms.TextInput(
                        attrs={'class': 'form-control mb-3',
                               'placeholder': 'Enter last name',
                               })
                    )
    address_line1 = forms.CharField(
                    required=True,
                    label='Street Address',
                    widget=forms.TextInput(
                        attrs={'class': 'form-control mb-3',
                               'placeholder': 'Enter street address',
                               })
                    )
    address_line2 = forms.CharField(
                    required=False,
                    label='Suburb',
                    widget=forms.TextInput(
                        attrs={'class': 'form-control mb-3',
                               'placeholder': 'Enter suburb',
                               })
                    )
    city = forms.CharField(
                    required=True,
                    label='City',
                    widget=forms.TextInput(
                        attrs={'class': 'form-control mb-3',
                               'placeholder': 'Enter city',
                               })
                    )
    province = forms.CharField(
                    required=True,
                    label='Province/State',
                    widget=forms.TextInput(
                        attrs={'class': 'form-control mb-3',
                               'placeholder': 'Enter province/state',
                               })
                    )
    country = forms.CharField(
                    required=True,
                    label='Country',
                    widget=forms.TextInput(
                        attrs={'class': 'form-control mb-3',
                               'placeholder': 'Enter country',
                               })
                    )
    postal_code = forms.CharField(
                    required=True,
                    label='Postal Code',
                    widget=forms.TextInput(
                        attrs={'class': 'form-control mb-3',
                               'placeholder': 'Enter postal code',
                               })
                    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(Field('first_name', value=self.user.first_name), css_class='form-group col-md-6'),
                Column(Field('last_name', value=self.user.last_name), css_class='form-group col-md-6'),
                css_class='row'
            ),
            Row(
                Column('address_line1', css_class='form-group col-md-6'),
                Column('address_line2', css_class='form-group col-md-6'),
                css_class='row'
            ),
            Row(
                Column('city', css_class='form-group col-md-6'),
                Column('province', css_class='form-group col-md-6'),
                css_class='row'
            ),
            Row(
                Column('country', css_class='form-group col-md-6'),
                Column('postal_code', css_class='form-group col-md-6'),
                css_class='row'
            ),
            # Submit('submit', 'Save', css_class="btn btn-primary me-2")
        )

    class Meta:
        model = Profile
        fields = ['address_line1', 'address_line2', 'city', 'province', 'country', 'postal_code']

    def save(self, *args, **kwargs):
        user = self.instance.user
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.save()
        profile = super(ProfileForm, self).save(*args, **kwargs)
        return profile


class ProfileImageForm(forms.ModelForm):
    profile_image = forms.ImageField(
                      required=True,
                      label='Upload Profile Image',
                      widget=forms.FileInput(attrs={'class': 'form-control'})
                      )

    class Meta:
        model = Profile
        fields = ['profile_image']


class MemberInviteForm(forms.ModelForm):
    first_name = forms.CharField(
                required=True,
                label='First Name',
                widget=forms.TextInput(
                    attrs={'class': 'form-control mb-3',
                            'placeholder': 'Enter first name',
                            })
                )
    last_name = forms.CharField(
                required=True,
                label='Last Name',
                widget=forms.TextInput(
                    attrs={'class': 'form-control mb-3',
                            'placeholder': 'Enter last name',
                            })
                )
    invite_email = forms.CharField(
                    required=True,
                    label='Invite Email',
                    widget=forms.EmailInput(
                        attrs={'class': 'form-control mb-3',
                               'placeholder': 'Enter email',
                               })
                    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(Field('first_name'), css_class='form-group col-md-12'),
            ),
            Row(
                Column(Field('last_name'), css_class='form-group col-md-12'),
                css_class='row'
            ),
            Row(
                Column(Field('invite_email'), css_class='form-group col-md-12'),
                css_class='row'
            ),
            Submit('submit', 'Send Invite', css_class="btn btn-primary me-2")
        )

    class Meta:
        model = MemberInvite
        fields = ['first_name', 'last_name', 'invite_email']

    # def save(self, *args, **kwargs):
    #     invite = self.instance
    #     user_profile = self.instance.profile
    #     invite.invite_email = self.cleaned_data.get('invite_email')
    #     invite.first_name = self.cleaned_data.get('first_name')
    #     invite.first_name = self.cleaned_data.get('first_name')
    #     invite.invited_by = user_profile.uniqueId
    #     invite.inviter_team = user_profile.user_team
    #     invite.invite_code = str(uuid4()).split('-')[4]
    #     invite.save()
    #     member_invite = super(MemberInviteForm, self).save(*args, **kwargs)
    #     return member_invite
