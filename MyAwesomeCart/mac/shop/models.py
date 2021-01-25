from django.db import models

# Create your models here.

#classname(Product) refers to table name so a table Product is created with columns i.e attributes under class
class Product(models.Model):
    prod_id = models.AutoField(primary_key=True, unique=True, blank=False)
    prod_name = models.CharField(max_length=50,default="name")
    prod_desc = models.CharField(max_length=300,default='desc')
    category=models.CharField(max_length=50,default='')
    sub_category=models.CharField(max_length=50,default='')
    price=models.IntegerField(default=0)
    publ_date = models.DateField()
    image=models.ImageField(upload_to="shop/images",default='')

    def __str__(self):
        return self.prod_name

class Contact(models.Model):
        msg_id = models.AutoField(primary_key=True,unique=True, blank=False)
        name = models.CharField(max_length=50, default="")
        email = models.CharField(max_length=70, default="")
        phone = models.CharField(max_length=70, default='')
        desc = models.CharField(max_length=500, default='')

        def __str__(self):
            return self.name

class Orders(models.Model):
    order_id=models.AutoField(primary_key=True)
    items_json=models.CharField(max_length=5000)
    name=models.CharField(max_length=90)
    email=models.CharField(max_length=111)
    phone = models.CharField(max_length=111,default="")
    amount=models.IntegerField(default=0)
    address = models.CharField(max_length=131)
    city= models.CharField(max_length=90)
    state=models.CharField(max_length=90)
    zip_code = models.CharField(max_length=90)
    # zip is inbuild func in django so write another name
    #itemsjson is our item names

class OrderUpdate(models.Model):
    update_id=models.AutoField(primary_key=True)
    order_id=models.IntegerField(default='')
    update_desc=models.CharField(max_length=5000)
    timestamp=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:7]+ "..."








