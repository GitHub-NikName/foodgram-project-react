from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.conf import settings


help_text = {}  # TODO: хз //собрать сюда или удалить.


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, first_name, last_name,
                     **extra_fields):
        """
        Create and save a user with the given username, email, first_name,
         last_name and password.
        """
        if not username:
            raise ValueError("The given username must be set")

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password, first_name, last_name,
                    **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password,
                                 first_name, last_name, **extra_fields)

    def create_superuser(self, username, email=None, password=None,
                         **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        first_name = None
        last_name = None

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password,
                                 first_name, last_name, **extra_fields)


class User(AbstractUser):
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    password = models.CharField(_("password"), max_length=150)
    email = models.EmailField(
        _("email address"),
        max_length=254,
        unique=True,
        error_messages={
            'unique':
                'Пользователь с таким адресом электронной почты уже существует'
        },
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return '%s(%s, %s)' % (type(self).__name__, self.pk, self.username)

    def __repr__(self):
        return self.__str__()



# TODO хелп текст в словарь?
# TODO подправить локализацию???
