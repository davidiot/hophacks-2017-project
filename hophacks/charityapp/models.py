from django.db import models
from django.contrib.auth.models import User
# from django.db.models.signals import post_save
# from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_id = models.TextField()
    charity_account_id = models.TextField(default="")

    class Meta:
        ordering = ('customer_id',)


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()


class Sector(models.Model):
    national_average = models.DecimalField(max_digits=20, decimal_places=2)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ('name',)


class Charity(models.Model):
    merchant_id = models.TextField()
    picture = models.TextField()
    description = models.TextField()
    link = models.TextField()
    email = models.EmailField()
    name = models.CharField(max_length=100)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)

    class Meta:
        ordering = ('name',)


class Link(models.Model):
    purchase_id = models.TextField()
    transfer_id = models.TextField()
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    merchant = models.TextField()
    date = models.DateField()
    purchase_amount = models.DecimalField(max_digits=20, decimal_places=2)
    transfer_amount = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        ordering = ('sector',)


class Rule(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=6, decimal_places=4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('sector',)


class Suggestion(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    picture = models.TextField()
    name = models.CharField(max_length=100)
    description = models.TextField()
    rule_creator = models.BooleanField(default=False)
    threshold = models.DecimalField(max_digits=6, decimal_places=4)

    class Meta:
        ordering = ('-threshold', 'sector', 'name')


class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    purchase_id = models.TextField()
