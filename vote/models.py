from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils.safestring import mark_safe
from django.contrib.auth.models import AbstractUser


class UserManager(BaseUserManager):
    def create_user(self, id, password, *args, **kwargs):
        if not id:
            raise ValueError('Users must have an identifier')
        if not password:
            raise ValueError('Users must have a password')

        user = self.model(
            id=id,
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, id, password):
        user = self.create_user(
            id,
            password=password,
        )
        user.is_superuser = True
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None
    id = models.CharField(max_length=40, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    birthdate = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255)
    district = models.CharField(max_length=100)
    email = models.EmailField()

    objects = UserManager()

    USERNAME_FIELD = 'id'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.id

    def check_password(self, raw_password):
        return super().check_password(raw_password)

    def set_password(self, raw_password):
        super().set_password(raw_password)


class District(models.Model):
    short_name = models.CharField(max_length=10)
    long_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.short_name} - {self.long_name}"


class Term(models.Model):
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.start.year} - {self.end.year}"


class Candidate(models.Model):
    _id = models.AutoField(primary_key=True)
    id = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=100)
    birthdate = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    description = models.TextField(null=True, blank=True)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    votes = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return f"{self.name} - {self.district}"

    def image_tag(self):
        return mark_safe('<img src="/media/%s" width="150" style="max-height: 200px;object-fit: cover;" />' % self.image)

    def get_vote_count(self):
        votes = Vote.objects.filter(candidate=self.id).values_list('user', flat=True)
        votes = votes.distinct()
        print(votes)
        return votes.count()

    image_tag.short_description = 'Image'


class Vote(models.Model):
    user = models.CharField(max_length=40)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, to_field='id')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} voted for {self.candidate}"

    def count(self):
        return Vote.objects.filter(candidate=self.candidate).count()

    def save(self, *args, **kwargs):
        # # TODO: add encryption here
        # # self.candidate.id = self.candidate.id + 1
        # print("Saving Vote:", self.candidate, self.user)
        super().save(*args, **kwargs)

        # Increment the candidate's vote count
        # candidate = Candidate.objects.get(id=self.candidate)
        # candidate.votes += 1
        # candidate.save()
