from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.http import JsonResponse
from .models import Product, Category, Supplier

class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(in_stock=True).select_related('category', 'supplier')
        category_slug = self.request.GET.get('category')
        supplier_id = self.request.GET.get('supplier')
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['suppliers'] = Supplier.objects.filter(is_active=True)
        context['current_category'] = self.request.GET.get('category', None)
        context['current_supplier'] = self.request.GET.get('supplier', None)
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'

    def get_object(self):
        return get_object_or_404(Product.objects.select_related('category', 'supplier'), slug=self.kwargs['slug'])


class SupplierMapView(TemplateView):
    """Представление для отображения интерактивной карты поставщиков"""
    template_name = 'products/supplier_map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suppliers'] = Supplier.objects.filter(is_active=True)
        return context


def suppliers_json(request):
    """API endpoint для получения данных о поставщиках в формате JSON"""
    from django.db.models import Count
    suppliers = Supplier.objects.filter(is_active=True).annotate(products_count=Count('products'))
    data = []
    for supplier in suppliers:
        data.append({
            'id': supplier.id,
            'name': supplier.name,
            'description': supplier.description,
            'address': supplier.address,
            'latitude': float(supplier.latitude),
            'longitude': float(supplier.longitude),
            'phone': supplier.phone,
            'email': supplier.email,
            'website': supplier.website,
            'image': supplier.image.url if supplier.image else None,
            'products_count': supplier.products_count,
        })
    return JsonResponse(data, safe=False)