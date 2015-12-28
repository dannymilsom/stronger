from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse

from ..managers import DailyNutritionManager


class DailyNutrition(models.Model):
    """Nutritional record of the food consumed by a user on a given day."""

    date = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    calories = models.IntegerField()
    protein = models.IntegerField()
    carbs = models.IntegerField()
    fats = models.IntegerField()
    created_on = models.DateTimeField()

    objects = DailyNutritionManager()

    def __unicode__(self):
        return "{}".format(self.id)

    def get_absolute_url(self):
        """Returns a canonical URL for a DailyNutrition instance."""
        return reverse('meal', kwargs={'meal_id': self.id})

    def newsfeed_category(self):
        return 'nutrition'

    def newsfeed_message(self):
        return "Consumed {} calories".format(self.calories)
