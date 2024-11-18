from django.contrib.auth.models import UserManager
from django.db import models
from django.db.models import Count, Exists, F, OuterRef, Q
from django.db.models.functions import Coalesce
from django.utils.timezone import now


class TagManager(models.QuerySet):
    def annotate_is_selected(self, user):
        return self.model.objects.all().annotate(is_selected=Exists(user.tags.filter(id=OuterRef('id'))))


class NotificationManager(models.QuerySet):
    def annotate_has_been_seen(self, user):
        return self.annotate(
            has_been_seen=Exists(user.notifications.filter(notification__id=OuterRef('id'), has_been_seen=True))
        )


class CustomUserQueryset(models.QuerySet):
    def annotate_num_of_past_travels(self):
        return self.annotate(num_of_past_travels=Count(F('travels'), filter=Q(travels__end_date__lte=now().date())))

    def annotate_num_of_upcoming_travels(self):
        return self.annotate(
            num_of_upcoming_travels=Count(F('travels'), filter=Q(travels__initial_date__gte=now().date()))
        )

    def annotate_num_of_travels(self):
        return self.annotate_num_of_upcoming_travels().annotate_num_of_past_travels()

    def annotate_visited_places(self):
        return self.annotate(
            visited_places=Coalesce(
                Count(F('travels__stops'), filter=Q(travels__end_date__lte=now(), travels__stops__type='place')), 0
            )
        )

    def annotate_visited_events(self):
        return self.annotate(
            visited_events=Coalesce(
                Count(F('travels__stops'), filter=Q(travels__end_date__lte=now(), travels__stops__type='event')), 0
            )
        )

    def annotate_travel_variables(self):
        return self.annotate_num_of_travels().annotate_visited_places().annotate_visited_events()


class CustomUserManager(UserManager):
    def get_queryset(self):
        return CustomUserQueryset(model=self.model, using=self.db)
