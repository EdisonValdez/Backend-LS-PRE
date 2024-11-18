import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, Group
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField

from local_secrets.cities.models import City
from local_secrets.languages.models import Language
from local_secrets.messaging.providers import FCMProvider
from local_secrets.users.managers import CustomUserManager, NotificationManager, TagManager


class CustomUser(AbstractUser):
    tags = models.ManyToManyField('Tag', through='UserTags', verbose_name=_('Tags'))
    phone_prefix = models.CharField(max_length=10, verbose_name=_('Prefix'))
    phone = models.CharField(max_length=18, verbose_name=_('Phone'))
    profile_picture = ThumbnailerImageField(upload_to='pfp', verbose_name=_('Profile Picture'))
    device_id = models.CharField(max_length=512, verbose_name=_('Device ID'), null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)

    objects = CustomUserManager()

    def update_tags(self, tags):
        self.tags.set(tags)

    def update_pfp(self, file):
        self.profile_picture = file[0]
        self.save()

    def send_notification(self, notification):
        return FCMProvider.send_notification_to_device(
            title=notification.title, body=notification.body, device_id=self.device_id
        )

    def restore_password(self):
        new_password = f'{uuid.uuid4().hex[:8].upper()}$'
        send_mail(
            subject='Password recovery',
            message=f'Your new generated password is: {new_password}',
            from_email='tech@localsecrets.travel',
            recipient_list=[self.email],
            fail_silently=False,
        )
        self.set_password(new_password)
        self.save()

    def save(self, *args, **kwargs):
        return super(CustomUser, self).save(*args, **kwargs)


class Tag(models.Model):
    title = models.CharField(max_length=120, verbose_name=_('Tag'))

    objects = TagManager.as_manager()

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self):
        return self.title

    def display_text(self, field, language='en'):
        try:
            return getattr(self.translations.get(language__code=language), field)
        except BaseException:
            return getattr(self, field)


class TranslatedTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    title = models.CharField(max_length=120, verbose_name=_('Translated Tag'))


class UserTags(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('User'))
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name=_('Tag'), related_name='users')

    class Meta:
        verbose_name = _('User Preference')
        verbose_name_plural = _('Users Preferences')

    def __str__(self):
        return f'{self.user.username} - {self.tag.title}'


class Notification(models.Model):
    from local_secrets.sites.models import Site

    created_at = models.DateTimeField(auto_now=True, verbose_name=_('Created at'))
    title = models.CharField(max_length=150, verbose_name=_('Title'))
    body = models.TextField(verbose_name=_('Body'))
    site = models.ForeignKey(Site, null=True, on_delete=models.SET_NULL, verbose_name=_('Site'))
    link = models.CharField(max_length=500, null=True, blank=True)

    objects = NotificationManager.as_manager()

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')

    # Mark notification as seen for user
    def mark_as_seen(self, user):
        # Get or create notification relation
        user_notification, created = UserNotification.objects.get_or_create(user=user, notification=self)
        #  Update State to seen/True
        user_notification.has_been_seen = True
        #  Save relation
        user_notification.save()

    def save(self, *args, **kwargs):
        users = CustomUser.objects.all()
        notification = super(Notification, self).save(*args, **kwargs)
        notification_list = []
        for user in users:
            if UserNotification.objects.filter(user=user, notification=self).exists():
                continue
            notification_list.append(UserNotification(user=user, notification=self))
            user.send_notification(self)
        UserNotification.objects.bulk_create(notification_list)
        return notification


class UserNotification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications', verbose_name=_('User'))
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, related_name='users', verbose_name=_('Notification')
    )
    has_been_seen = models.BooleanField(default=False, verbose_name=_('Has been seen'))

    class Meta:
        verbose_name = _('Users Notification')
        verbose_name_plural = _('Users Notifications')


class Ambassador(CustomUser):
    cities = models.ManyToManyField(City)

    class Meta:
        verbose_name = _('Ambassador')
        verbose_name_plural = _('Ambassadors')

    def save(self, *args, **kwargs):
        created = False if self.id else True
        super(Ambassador, self).save(*args, **kwargs)
        if created:
            self.is_staff = True
            self.groups.add(Group.objects.get(id=2))
        res = super(Ambassador, self).save(*args, **kwargs)
        return res


class GroupDescription(models.Model):
    description = models.TextField(verbose_name=_('Description'))

    group = models.OneToOneField(Group, on_delete=models.CASCADE)

    def display_text(self, field, language='en'):
        try:
            return getattr(self.translations.get(language__code=language), field)
        except BaseException:
            if field == 'name':
                return self.group.name
            return getattr(self, field)


class TranslatedGroupDescription(models.Model):
    group_description = models.ForeignKey(GroupDescription, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    description = models.TextField(verbose_name=_('Translated Description'))
    name = models.CharField(max_length=150, verbose_name=_('Translated Name'))
