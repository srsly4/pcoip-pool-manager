from django import forms

from . import models as app_models


class PoolForm(forms.ModelForm):
    class Meta:
        model = app_models.Pool
        fields = ('pool_id', 'displayName', 'description', 'maximumCount', 'enabled',)


class MultiplePoolForm(PoolForm):
    pool_data_file = forms.FileField(required=True)

    class Meta(PoolForm.Meta):
        fields = ('pool_data_file',)


class MultiplePool(app_models.Pool):
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        pass

    class Meta:
        proxy = True
        managed = False
