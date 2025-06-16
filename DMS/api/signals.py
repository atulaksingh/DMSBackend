from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.text import slugify
from django.conf import settings

from .models import Owner, CustomUser
from .utils import generate_token

@receiver(post_save, sender=Owner)
def create_user_when_owner_created(sender, instance, created, **kwargs):
    if created and instance.email and instance.owner_name:
        name = instance.owner_name.strip().lower()
        # generated_password = name[:4] + "@123"
        name_part = name[:4].lower()
        generated_password = f"{name_part}@123"

        user = CustomUser.objects.create_user(
            username=instance.email,  # Use email as username
            email=instance.email,
            name=instance.owner_name,
            password=generated_password,
            client=instance.client,
            is_active=True  # Force user to be inactive at first
        )
        print(f"Generated password for {user.email}: {generated_password}")

        # Assign created user to Owner
        instance.user = user

        # Temporarily disconnect signal to avoid triggering update below
        from django.db.models.signals import post_save
        post_save.disconnect(update_user_when_owner_updated, sender=Owner)


        instance.save(update_fields=["user"])
        post_save.connect(update_user_when_owner_updated, sender=Owner)

        #   Send activation email
        subject = "Activate Your Account"
        message = render_to_string(
            'activate.html',
            {
                'user': user,
                'domain': '127.0.0.1:8000',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user),
            }
        )
        email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [instance.email])
        email.send()


# UPDATE signal — only handles update on existing Owner
# @receiver(post_save, sender=Owner)
# def update_user_when_owner_updated(sender, instance, created, **kwargs):
#     if not created and instance.user:
#         user = instance.user
#         user.name = instance.owner_name
#         user.email = instance.email
#         user.username = instance.email
#         user.client = instance.client

#         if not instance.is_active:
#             user.is_active = False
#             print(f"Deactivating user since owner '{instance.owner_name}' is inactive")
#         elif instance.is_active and not user.is_active:
#             user.is_active = True
#             print(f"Activating user since owner '{instance.owner_name}' is now active")

#         user.save()


@receiver(post_save, sender=Owner)
def update_user_when_owner_updated(sender, instance, created, **kwargs):
    if not created and instance.user:
        user = instance.user
        has_changes = False

        if user.name != instance.owner_name:
            user.name = instance.owner_name
            has_changes = True

        if user.email != instance.email:
            user.email = instance.email
            user.username = instance.email
            has_changes = True

        if user.client != instance.client:
            user.client = instance.client
            has_changes = True

        if not instance.is_active and user.is_active:
            user.is_active = False
            has_changes = True
            print(f"Deactivating user since owner '{instance.owner_name}' is inactive")
        elif instance.is_active and not user.is_active:
            user.is_active = True
            has_changes = True
            print(f"Activating user since owner '{instance.owner_name}' is now active")

        if has_changes:
            user.save()
