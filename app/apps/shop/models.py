from typing import Iterable, Optional
from django.db import models
# Only works on relative path, if it will be absolute path module cannot be imported because of
# apps not a package and cannot be it
from ..users.models import User

STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен')
)


class Shop(models.Model):
    name = models.CharField(max_length=30, verbose_name='Название')
    url = models.URLField(verbose_name='Ссылка', blank=True, help_text='<i>Введите URL сайта</i>')
    owner = models.OneToOneField(User, verbose_name='Владелец', on_delete=models.CASCADE, blank=True)
    state = models.BooleanField(verbose_name='Статус получения заказа', blank=True, default=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Список магазинов'
        ordering = ('-name',)

    def __str__(self):
        return f'{self.name}'


class Category(models.Model):
    name = models.CharField(max_length=30, verbose_name='Название')
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Список категорий'
        ordering = ('-name',)

    def __str__(self):
        return f'{self.name}'

    # Bypassing ManyToMany restriction in admin.py
    def get_category(self): return " | ".join([str(p) for p in self.shops.all()])


class Product(models.Model):
    name = models.CharField(max_length=30, verbose_name='Название')
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products', blank=True,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Список продуктов'
        ordering = ('-name',)

    def __str__(self):
        return f'{self.name} | {self.category}'


class ProductInfo(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    model = models.CharField(max_length=80, verbose_name='Модель', blank=True)
    product = models.ForeignKey(Product, verbose_name='Продукт', related_name='product_infos', blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='product_infos', blank=True,
                             on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name='Количество')
    price = models.FloatField(verbose_name='Цена')
    price_rrc = models.FloatField(verbose_name='Рекомендуемая розничная цена')
    parameters = models.JSONField(verbose_name='Параметры')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информационный список о продуктах'
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop'], name='unique_product_info'),
        ]
        ordering = ('-name',)

    def __str__(self):
        return f'{self.name} | {self.model} | {self.product} | {self.shop} | {self.quantity} | {self.price} | {self.price_rrc} | {self.parameters}'


# не уверен насчёт логики создания отдельной модели для параметров товара

# class Parameter:
#     name = models.CharField(max_length=30, verbose_name='Название')
class Contact(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', related_name='contacts', on_delete=models.CASCADE)
    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Список контактов'

    def __str__(self):
        return f'{self.user} {self.city} {self.street} {self.house}'


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name='Покупатель', related_name='orders', on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name='Дата заказа', auto_now=True)
    state = models.CharField(max_length=20, verbose_name='Статус', choices=STATE_CHOICES)
    contact = models.ForeignKey(Contact, verbose_name='Контакт', related_name='orders', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Список заказов'
        ordering = ('-date',)

    def __str__(self):
        return f'{str(self.date)} | {self.user} | {self.state} | {self.contact}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='order_items', on_delete=models.CASCADE)
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте', related_name='ordered_items',
                                     on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество', default=0)

    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = 'Список заказанных товаров'
        constraints = [
            models.UniqueConstraint(fields=['order_id', 'product_info'], name='unique_order_item')
        ]

    def __str__(self):
        return f'{self.order} | {self.quantity}'


class BasketItem(models.Model):
    product = models.ForeignKey(ProductInfo, verbose_name='Продукт', related_name='cart_product', blank=True,
                                on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='Пользователь', related_name='cart_user', on_delete=models.CASCADE)
    price = models.FloatField(verbose_name='Цена за отдельный товар', default=0)
    quantity = models.PositiveIntegerField(verbose_name='Количество', default=1)
    
    class Meta:
        verbose_name = 'Товар в пользовательской корзине'
        verbose_name_plural = 'Товары в пользовательской корзине'
    
    def increase_quantity_and_price(self, n: int = 1) -> None:
        if self.quantity + n > self.product.quantity:
            raise ValueError("This product has been sold") 
        self.quantity += n
        self.recalculate_price()
        
    def decrease_quantity_and_price(self, n: int = 1) -> None:
        if self.quantity - n <= 0:
            self.delete()
        else:
            self.quantity -= n
            self.recalculate_price()       
        
    def recalculate_price(self) -> None:
        self.price = self.product.price * self.quantity
        self.save() 
    
    def __str__(self):
        return f'{self.product} | {self.user} | {self.quantity}'

class Basket(models.Model):
    basket_items = models.ManyToManyField(BasketItem, verbose_name='Товары', related_name='basket_items', blank=True)
    user = models.OneToOneField(User, verbose_name='Пользователь', related_name='basket_user', on_delete=models.CASCADE)
    final_price = models.FloatField(verbose_name='Цена в корзине', default=0)

    
    class Meta:
        verbose_name = 'Корзина пользователя'
        verbose_name_plural = 'Список пользовательских корзин'
    
    def calculate_final_price(self):
        self.final_price = 0
        for item in self.basket_items.all():
            self.final_price += item.price
        self.save()
            
    def __str__(self):
        return f'{self.user} | {self.final_price}'

