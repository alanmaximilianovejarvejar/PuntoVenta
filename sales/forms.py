from django import forms


class SaleFilterForm(forms.Form):
    start = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date", "aria-label": "Fecha inicial"}))
    end = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date", "aria-label": "Fecha final"}))
    folio = forms.CharField(required=False, max_length=32, widget=forms.TextInput(attrs={"placeholder": "Folio"}))


class VoidSaleForm(forms.Form):
    reason = forms.CharField(max_length=240, widget=forms.TextInput(attrs={"placeholder": "Motivo de cancelacion"}))
