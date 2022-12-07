from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import OuterRef, F, Value
from django.db.models.functions import JSONObject, Concat

from courses.models import Permission


class UserMixin:
    @staticmethod
    def annotation():
        courses_list = Permission.objects.filter(user_id=OuterRef("pk"), course__isnull=False). \
                annotate(data=JSONObject(access=F('access'), name=F('course__name'), slug=F('course__slug'))).\
                values_list("data").order_by('course__name', '-access')

        annotation = {
            "full_name": Concat('first_name', Value(' '), 'last_name'),
            "courses_list": ArraySubquery(courses_list)
        }
        return annotation
