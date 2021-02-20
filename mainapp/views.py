from django.shortcuts import render
from django.views.generic import DetailView, View, TemplateView
from .models import Notebook, Smartphone, Category, LatestProducts, Customer, Cart
from .mixins import CategoryDetailMixin
# Create your views here.

# def test_view(request):
#     categories = Category.objects.get_categories_for_left_sidebar()
#     return render(request, 'base.html', {'categories': categories})
class BaseView(View):
    def get(self, request, *args, **kwargs):        
        categories = Category.objects.get_categories_for_left_sidebar()
        products = LatestProducts.objects.get_products_for_main_page(
            'notebook', 'smartphone', with_respect_to='notebook'
            )
        context = {
            'categories': categories,
            'products': products
        }
        return render(request, 'base.html', context)

class ProductDetailView(CategoryDetailMixin, DetailView):

    CT_MODEL_MODEL_CLASS = {
        'notebook': Notebook,
        'smartphone': Smartphone
    }

    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)
    
    # model = Model
    # queryset = Model.object.all()
    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwargs = 'slug'


class CategoryDetailView(CategoryDetailMixin, DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'

class CartView(View):
    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        cart = Cart.objects.get(owner=customer)
        categories = Category.objects.get_categories_for_left_sidebar()
        context = {
            'cart': cart,
            'categories': categories
        }
        return render(request, 'cart.html', context)
