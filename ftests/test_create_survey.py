from .base import FunctionalTest

class CreateSurveyTest(FunctionalTest):
    def setUp(self):
        super(CreateSurveyTest, self).setUp()

    def test_create_survey(self):
        """ Create a new survey using a form """
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('id_survey_list').click()
        title = self.browser.find_element_by_tag_name('h1').text
        self.assertEquals('Surveys', title)
