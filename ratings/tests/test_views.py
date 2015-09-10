from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy

from ratings.models import Survey


class ViewTest(TestCase):
    survey_list_url = reverse('survey_list')

    def test_survey_list_view_renders_survey_list_template(self):
        response = self.client.get(self.survey_list_url)
        self.assertTemplateUsed(response, 'ratings/survey_list.html')

    def test_surveys_show_up_on_survey_list_page(self):
        num_surveys = 10
        expected_surveys = mommy.make(Survey, _quantity=num_surveys)
        response = self.client.get(self.survey_list_url)
        surveys = response.context['survey_list']
        self.assertEquals(len(surveys), num_surveys)
