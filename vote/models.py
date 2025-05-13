from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils.safestring import mark_safe
from django.contrib.auth.models import AbstractUser


class UserManager(BaseUserManager):
    def create_user(self, identifier, password, *args, **kwargs):
        if not identifier:
            raise ValueError('Users must have an identifier')
        if not password:
            raise ValueError('Users must have a password')

        user = self.model(
            identifier=identifier,
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, identifier, password):
        user = self.create_user(
            identifier,
            password=password,
        )
        user.is_superuser = True
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = None
    identifier = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=100)
    birthdate = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255)
    district = models.CharField(max_length=100)
    email = models.EmailField()

    objects = UserManager()

    USERNAME_FIELD = 'identifier'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.identifier

    def check_password(self, raw_password):
        """
        Check if the provided raw_password matches the user's stored password.
        """
        return super().check_password(raw_password)


class Candidate(models.Model):
    name = models.CharField(max_length=100)
    birthdate = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255)
    district = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    description = models.TextField(null=True, blank=True)
    term_start = models.DateField(null=True, blank=True)
    term_end = models.DateField(null=True, blank=True)
    votes = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return f"{self.name} - {self.district}"

    def image_tag(self):
        return mark_safe('<img src="/media/%s" width="150" style="max-height: 200px;object-fit: cover;" />' % self.image)

    image_tag.short_description = 'Image'


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='identifier')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} voted for {self.candidate}"

    def save(self, *args, **kwargs):
        # Increment the candidate's vote count
        self.candidate.votes += 1
        self.candidate.save()
        super().save(*args, **kwargs)
