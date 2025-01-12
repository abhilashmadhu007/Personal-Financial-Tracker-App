from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Users(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    income = models.IntegerField(null=True)

class Expert(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    exp= models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Expense(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    amount = models.IntegerField()
    date = models.DateField()
    category = models.CharField(max_length=30)

class Chat(models.Model):
    sender=models.CharField(max_length=20)
    receiver=models.CharField(max_length=20)
    date=models.DateTimeField(auto_now = True,null = True)
    message=models.CharField(max_length=400)


class Budget(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    amount = models.IntegerField()
    date = models.DateField()

class Update_Goal(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    amount = models.IntegerField() 
    

class Goal(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)
    goal = models.CharField(max_length=30)
    amount = models.IntegerField(null=True)
    set_amount = models.IntegerField(null=True)
    date = models.DateField(null=True)
 




