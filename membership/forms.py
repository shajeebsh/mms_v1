from django import forms

from .models import Member, MembershipDues, Payment


class WhatsAppMessageForm(forms.Form):
    members = forms.ModelMultipleChoiceField(
        queryset=Member.objects.all().order_by("first_name", "last_name"),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Select members to send the WhatsApp message to.",
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        required=True,
        help_text="Enter the message to send via WhatsApp.",
    )


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter membership_dues to the selected member's house dues
        if "member" in self.initial:
            member_id = self.initial["member"]
            # Get the selected member's house first
            member = Member.objects.filter(id=member_id).first()
            if member and member.house:
                self.fields["membership_dues"].queryset = MembershipDues.objects.filter(
                    house=member.house
                ).order_by("-year", "-month")
        elif "member" in self.data:
            try:
                member_id = int(self.data["member"])
                # Get the selected member's house first
                member = Member.objects.filter(id=member_id).first()
                if member and member.house:
                    self.fields["membership_dues"].queryset = (
                        MembershipDues.objects.filter(house=member.house).order_by(
                            "-year", "-month"
                        )
                    )
            except (ValueError, TypeError):
                pass
