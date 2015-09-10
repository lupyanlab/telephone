from django.core.urlresolvers import reverse
from django.test import TestCase


class ViewTest(TestCase):
    survey_list_url = reverse('survey_list')

    def test_survey_list_view_renders_survey_list_template(self):
        response = self.client.get(self.survey_list_url)
        self.assertTemplateUsed(response, 'ratings/survey_list.html')
