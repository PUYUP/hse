from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class ChoiceInlineForm(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        identifiers = ['A', 'B', 'C', 'D']
        kwargs['initial'] = [{'identifier': x} for x in identifiers]
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        total_true = 0
        
        for form in self.forms:
            if form.cleaned_data and form.cleaned_data.get('is_true') == True:
                total_true += 1

        if total_true > 1:
            raise ValidationError(_("Can't have multiple true choice."))

        if total_true == 0:
            raise ValidationError(_("Must select one true choice."))
