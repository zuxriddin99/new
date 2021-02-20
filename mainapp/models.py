from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse

User = get_user_model()

def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]

def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    
    return reverse(viewname, 
    kwargs={
        'ct_model': ct_model,
        'slug': obj.slug
        })


class MinResolutionErrorException(Exception):
    pass

class MaxResolutionErrorException(Exception):
    pass

class LatestProductsManager:
    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models =ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('id')[:5]
            products.extend(model_products) 
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(
                        products, 
                        key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to),
                        reverse=True
                    )
        return products 
 
class LatestProducts:

    objects = LatestProductsManager()

class CategoryManager(models.Manager):
    CATEGORY_NAME_COUNT_NAME = {
        'NoteBook': 'notebook__count',
        'SmartPhone': 'smartphone__count'
    }
    def get_queryset(self):
        return super().get_queryset()
    
    def get_categories_for_left_sidebar(self):
        models = get_models_for_count('notebook', 'smartphone')
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME_COUNT_NAME[c.name]))
            for c in qs
        ]
        return data
        # return [dict(name=c['name'], slug=c['slug'], count=c[self.CATEGORY_NAME_COUNT_NAME[c['name']]]) for c in qs]

        # category = Category.objects.all()
        # category.product.count
        # category.notebook
        # category.smartphone


class Category(models.Model):

    name = models.CharField(max_length=255, verbose_name="Имя категории")
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={'slug': self.slug})
    

class Product(models.Model):
    
    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name="Category", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Наименование") 
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name="Изображение")
    description = models.TextField(verbose_name="Описание", null=True)   
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")

    def __str__(self):
        return self.title

    # def save(self, *args, **kwargs):
    #     # image = self.image
    #     # img = Image.open(image)
    #     # new_img = img.convert('RGB')
    #     # resize_new_img = new_img.resize((200, 200), Image.ANTIALIAS)
    #     # filestream = BytesIO()
    #     # resize_new_img.save(filestream, 'JPEG', quality=98)
    #     # filestream.seek(8)
    #     # name = '{}.{}'.format(*self.image.name.split('.'))
    #     # self.image = InMemoryUploadedFile(
    #     #     filestream, 'ImageField', name, 'jpeg/image', sys.getsizeof(filestream), None
    #     # )

    #     image = self.image
    #     img = Image.open(image)
    #     min_height, min_width = self.MIN_RESALUTION
    #     max_height, max_widht = self.MAX_RESALUTION
    #     if img.height<min_height or img.width<min_width:
    #         raise MinResolutionErrorException('Rasm o`lchmdan juda kichkina')
    #     if img.height>max_height or img.width>max_width:
    #         raise MaxResolutionErrorException('Rasm o`lchmi juda katta')
    #     super().save(*args, **kwargs)

class Notebook(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Диагоналы')
    display_type = models.CharField(max_length=255, verbose_name='Тип дисплея')
    processor_freq = models.CharField(max_length=255, verbose_name='Частота процсессора')
    ram = models.CharField(max_length=255, verbose_name='Оперативная памят')
    video = models.CharField(max_length=255, verbose_name='Видеокарта')
    time_widhout_charge = models.CharField(max_length=255, verbose_name='Время работы аккумулятора')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)
    
    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')
    
class Smartphone(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Диагоналы')
    display_type = models.CharField(max_length=255, verbose_name='Тип дисплея')
    resolution = models.CharField(max_length=255, verbose_name='Разррешение екрана')
    accum_volume = models.CharField(max_length=255, verbose_name='Объем батареи')
    ram = models.CharField(max_length=255, verbose_name='Оперативная памят')
    sd = models.BooleanField(default=True, verbose_name="Наличие SD карты")
    sd_volume_max = models.CharField(
        max_length=255, null=True, blank=True, verbose_name='Максимальный объем встраивамо памяти'
        )
    main_cam_up = models.CharField(max_length=255, verbose_name='Главная камера')
    frontal_cam_up = models.CharField(max_length=255, verbose_name='Фронтальная камера')

    def __str__(self):
        return "{0} : {1}".format(self.category.name, self.title)
    
    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')

    # @property
    # def sd(self):
    #     if self.sd:
    #         return 'Да'
    #     return 'Нет'
    
class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Покупател', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая цена') 

    def __str__(self):
        return "Продукт {} (для корзины)".format(self.content_object.title)

class Cart(models.Model):
     owner = models.ForeignKey('Customer', verbose_name='Владелец', on_delete=models.CASCADE)
     product = models.ManyToManyField(CartProduct, blank=True ,related_name='related_cart')
     total_products = models.PositiveIntegerField(default=0)
     final_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая цена')
     in_order = models.BooleanField(default=False)
     for_anonymous_user = models.BooleanField(default=False)

     def __str__(self):
         return str(self.id)

class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.CharField(max_length=100, verbose_name='Адрес')
    
    def __str__(self):
        return "Покупатель: {} {}".format(self.user.first_name, self.user.last_name)

# class Specifiction(models.Model):
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     name = models.CharField(max_length=255, verbose_name='imya xarakteristika tovari')
    
#     def __str__(self):
#         return "Xarakteristika dlya tovari {}".format(self.name)
    
# class SomeModle(models.Model):
#     image = models.ImageField()

#     def __str__(self):
#         return str(self.id)
    