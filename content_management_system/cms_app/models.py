from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


class BaseUser(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    city = models.CharField(max_length=15, null=True, blank=True)
    contact_no = PhoneNumberField()

    def __str__(self) -> str:
        return self.username


class Blog(models.Model):
    owner = models.ForeignKey(BaseUser, on_delete=models.CASCADE)
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150)
    description = models.TextField()
    content = models.TextField()
    creation_date = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now_add=True)
    is_public = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.title + ' - ' + self.owner.name

class Like(models.Model):
    post = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(BaseUser, on_delete=models.CASCADE)
    like_id = models.AutoField(primary_key=True)

    def __str__(self) -> str:
        return self.user.name + ' liked ' + self.post.title + ' by ' + self.post.owner.name
    