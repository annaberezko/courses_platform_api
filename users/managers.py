from django.contrib.auth.base_user import BaseUserManager

from users.choices_types import ProfileRoles


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, role, send_mail, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        if send_mail:
            user.send_invitation_link()
        return user

    def create_user(self, email=None, password=None, role=ProfileRoles.LEARNER, **extra_fields):
        return self._create_user(email, password, role, True, **extra_fields)

    def create_superuser(self, email, password, role=ProfileRoles.SUPERUSER, **extra_fields):
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, role, False, **extra_fields)
