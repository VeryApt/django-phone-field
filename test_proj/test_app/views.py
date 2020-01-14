from django.views.generic.edit import FormView
from .forms import RequiredInputsForm


class FormView1(FormView):
    template_name = 'form_view_1.html'
    form_class = RequiredInputsForm
    success_url = '/form_view_1/success/'

