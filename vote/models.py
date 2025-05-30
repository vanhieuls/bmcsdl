from django.contrib import admin
from django.contrib.auth.base_user import BaseUserManager
from django.db import models, connection
from django.utils.functional import SimpleLazyObject
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
    name = models.CharField(max_length=1000)
    birthdate = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True)
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
        super().set_password(raw_password)

    def save(self, *args, **kwargs):
        if not self.password:
            self.set_password(None)

        # if user exists
        if self.name is None:
            return
        if self._state.adding:
            with connection.cursor() as cursor:
                cursor.execute(
                    'EXECUTE dbo.SP_InsertEncryptedUser @id = %s, @name = %s, @birthdate = %s, @address = %s, @district_id = %s, @email = %s, @password = %s, @last_login = %s, @is_superuser = %s, @is_staff = %s, @is_active = 1',
                    [self.id, self.name, self.birthdate, self.address, self.district_id, self.email, self.password, self.last_login, self.is_superuser, self.is_staff]
                )
        else:
            with connection.cursor() as cursor:
                cursor.execute(
                    'EXECUTE dbo.SP_UpdateEncryptedUser @id = %s, @name = %s, @birthdate = %s, @address = %s, @district_id = %s, @email = %s, @password = %s, @last_login = %s, @is_superuser = %s, @is_staff = %s, @is_active = 1',
                    [self.id, self.name, self.birthdate, self.address, self.district_id, self.email, self.password, self.last_login, self.is_superuser, self.is_staff]
                )

    def get_voted(self):
        with connection.cursor() as cursor:
            cursor.execute('EXECUTE dbo.SP_GetFinalVoteByUser @user_id = %s', [self.id])
            if cursor.description:
                result = cursor.fetchone()
                if result is None:
                    return False
                return result[0]
        return False

    @classmethod
    def from_db(cls, db, field_names, values):
        user = super().from_db(db, field_names, values)
        with connection.cursor() as cursor:
            cursor.execute('EXECUTE dbo.SP_SelectDecryptedUserById @id = %s', [user.id])
            row = cursor.fetchone()
            if row:
                user.id = row[0]
                user.name = row[1]
                user.birthdate = row[2]
                user.address = row[3]
                user.district_id = row[4]
                user.email = row[5]
                user.last_login = row[6]
                user.is_superuser = row[7]
                user.is_staff = row[8]
                user.is_active = row[9]
                user.date_joined = row[10]
                user.voted = row[11]
        return user


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

    def __str__(self):
        return f"{self.name} - {self.district}"

    def image_tag(self):
        return mark_safe('<img src="/media/%s" width="150" style="max-height: 200px;object-fit: cover;" />' % self.image)

    @admin.display(description="Votes")
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

        User.objects.filter(id=self.user).update(voted=True)

    def save(self, *args, **kwargs):
        # # # TODO: add encryption here
        # super().save(*args, **kwargs)
        pass
