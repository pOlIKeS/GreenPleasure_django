from django.db import models
from django.urls import reverse
import re

class Supplier(models.Model):
    """Модель поставщика с геолокацией"""
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    address = models.CharField(max_length=300, verbose_name="Адрес")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Долгота")
    image = models.ImageField(upload_to='suppliers/', blank=True, null=True, verbose_name="Изображение")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="Email")
    website = models.URLField(blank=True, verbose_name="Сайт")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:supplier_map')


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Изображение")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            # Транслитерация для русских символов
            translit_map = {
                'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
                'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
                'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '',
                'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
                ' ': '-', '"': '', "'": ''
            }
            
            # Преобразуем название в транслит
            slug = self.name.lower()
            for rus, eng in translit_map.items():
                slug = slug.replace(rus, eng)
            
            # Удаляем специальные символы и оставляем только буквы, цифры и дефисы
            slug = re.sub(r'[^a-z0-9\-]', '', slug)
            
            # Убираем повторяющиеся дефисы
            slug = re.sub(r'-+', '-', slug)
            
            # Убираем дефисы в начале и конце
            slug = slug.strip('-')
            
            self.slug = slug if slug else 'category'
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    supplier = models.ForeignKey(
        'Supplier', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Поставщик", related_name='products'
    )
    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Изображение")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    weight = models.CharField(max_length=50, verbose_name="Вес")
    calories = models.CharField(max_length=50, verbose_name="Калории")
    protein = models.CharField(max_length=50, verbose_name="Белки")
    fat = models.CharField(max_length=50, verbose_name="Жиры")
    carbs = models.CharField(max_length=50, verbose_name="Углеводы")
    in_stock = models.BooleanField(default=True, verbose_name="В наличии")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.slug])

    def formatted_price(self):
        return f"{self.price} ₽"

    def save(self, *args, **kwargs):
        if not self.slug:
            # Транслитерация для русских символов
            translit_map = {
                'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
                'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
                'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '',
                'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
                ' ': '-', '"': '', "'": ''
            }
            
            # Преобразуем название в транслит
            slug = self.name.lower()
            for rus, eng in translit_map.items():
                slug = slug.replace(rus, eng)
            
            # Удаляем специальные символы и оставляем только буквы, цифры и дефисы
            slug = re.sub(r'[^a-z0-9\-]', '', slug)
            
            # Убираем повторяющиеся дефисы
            slug = re.sub(r'-+', '-', slug)
            
            # Убираем дефисы в начале и конце
            slug = slug.strip('-')
            
            # Если slug пустой, используем 'product'
            if not slug:
                slug = 'product'
            
            # Проверяем уникальность и добавляем счетчик при необходимости
            base_slug = slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        super().save(*args, **kwargs)