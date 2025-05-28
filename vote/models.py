from django.contrib.auth.base_user import BaseUserManager
from django.db import models, connection
from django.utils.safestring import mark_safe
from django.contrib.auth.models import AbstractUser


def validate_id(value: str):
    if len(value) < 3:
        raise ValueError("ID must be at least 3 characters long")
    return True


class District(models.Model):
    short_name = models.CharField(max_length=10)
    long_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.short_name} - {self.long_name}"


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
    id = models.CharField(max_length=40, unique=True, primary_key=True, validators=[validate_id])
    name = models.CharField(max_length=100)
    birthdate = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    email = models.EmailField()
    voted = models.BooleanField(default=False, editable=False)

    objects = UserManager()

    USERNAME_FIELD = 'id'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.id

    def check_password(self, raw_password):
        return super().check_password(raw_password)

    def set_password(self, raw_password):
        if raw_password is None:
            raw_password = self.birthdate.strftime("%d%m%Y")
        print("Setting password for user:", self.id, "with raw password:", raw_password)
        super().set_password(raw_password)

    def save(self, *args, **kwargs):
        if not self.password:
            self.set_password(None)

        super().save(*args, **kwargs)


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
        with connection.cursor() as cursor:
            cursor.execute('EXECUTE dbo.SP_CountFinalVotesByCandidate @candidate_id = %s', [self.id])
            if cursor.description:
                return cursor.fetchone()[0]
        return 0

    image_tag.short_description = 'Image'


class Vote(models.Model):
    user = models.CharField(max_length=4000)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, to_field='id')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} voted for {self.candidate}"

    def count(self):
        return Vote.objects.filter(candidate=self.candidate).count()

    def cast_vote(self):
        with connection.cursor() as cursor:
            cursor.execute('use VOTE; EXECUTE dbo.SP_InsertEncryptedVote @user = %s, @candidate_id = %s', [self.user, self.candidate.id])

    def save(self, *args, **kwargs):
        # # # TODO: add encryption here
        # super().save(*args, **kwargs)
        pass
