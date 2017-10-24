from crispy_forms.bootstrap import AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Reset, Submit, ButtonHolder, HTML, Hidden
from django.forms import ModelForm, DateInput

from home.models import ClubDetails


class DetailsForm(ModelForm):

    helper = FormHelper()
    helper.label_class = 'col-sm-3'
    helper.field_class = 'col-sm-9'
    helper.form_show_errors = True

    helper.layout = Layout(
        Hidden(name='hidden_details', value=1, css_class='input-sm'),
        AppendedText('start_date', '<i class="fa fa-calendar"></i>', css_class='input-sm date-input'),
        AppendedText('monthly_contribution', 'UGX', css_class='input-sm'),
        ButtonHolder(
            HTML(
                '<button type="button" class="btn btn-default pull-right" data-dismiss="modal">Close</button>'
                '<button type="submit" class="btn btn-primary pull-right">Submit changes</button>'
            ),
        ),
    )

    class Meta:
        fields = '__all__'
        model = ClubDetails
        widgets = {
            'start_date': DateInput(format='%Y-%m-%d')
        }
