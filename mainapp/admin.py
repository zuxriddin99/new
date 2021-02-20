from django.contrib import admin
from django.forms import ModelChoiceField, ModelForm
from .models import *

class SmartphoneAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if not instance.sd:
            self.fields['sd_volume_max'].widget.attrs.update({
                'readonly': True,
                'style': 'backgraund: lightgray;'
            })

    def clean(self):
        if not self.cleaned_data['sd']:
            self.cleaned_data['sd_volume_max'] = None
        return self.cleaned_data


# class NotebookAdminForm(ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['image'].help_text=mark_safe(
    #         '<span style="color:red; font-size: 15px;">Razmer o`lchamlari maxsimal {}x{} shunday bo`lishi kerak</span>'.format(
    #             *Product.MIN_RESALUTION
    #             )
    #         )

    # def clean_image(self):
    #     image = self.cleaned_data['image']
    #     img = Image.open(image)
    #     min_height, min_width = Product.MIN_RESALUTION
    #     max_height, max_widht = Product.MAX_RESALUTION
    #     if image.size >Product.MAX_IMAGE_SIZE:
    #         raise ValidationError('Foto surat razmeri 3 MB bo`lishi kerak!')

    #     if img.height<min_height or img.width<min_width:
    #         raise ValidationError('Rasm o`lchmdan juda kichkina')
        
    #     if img.height>max_height or img.width>max_width:
    #         raise ValidationError('Rasm o`lchmi juda katta')
    #     return image

class NotebookAdmin(admin.ModelAdmin):
    # form = NotebookAdminForm
    def formfield_for_foreignkey(self, db_filed, request, **kwargs):
        if db_filed.name =='category':
            return ModelChoiceField(Category.objects.filter(slug='notebooks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class SmartphoneAdmin(admin.ModelAdmin):

    change_form_template = 'admin.html'
    form = SmartphoneAdminForm

    def formfield_for_foreignkey(self, db_filed, request, **kwargs):
        if db_filed.name =='category':
            return ModelChoiceField(Category.objects.filter(slug='smartphone'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Register your models here.
admin.site.register(Category)
admin.site.register(Notebook, NotebookAdmin)
admin.site.register(Smartphone, SmartphoneAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)