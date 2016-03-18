import time
import sys
from unipath import Path

from django.conf import settings
from django.core.files import File
from django.test import LiveServerTestCase, override_settings

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from grunt.models import Game, Chain, Message
from ratings.forms import NewSurveyForm

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT, MEDIA_URL = '/media-test/')
class FunctionalTest(LiveServerTestCase):
    def setUp(self):
        super(FunctionalTest, self).setUp()
        self.browser = None
        self.new_user()

    def tearDown(self):
        super(FunctionalTest, self).tearDown()

        if self.browser:
            self.browser.quit()

        TEST_MEDIA_ROOT.rmtree()

    def create_game(self, name, nchains=1, depth=0, num_seeds_per_chain=1):
        """Create a game with the specified number of chains.

        Args:
            name: The name of the game to create.
            nchains: The number of chains to add to the game. Names for the
                chains are created automatically.
            depth: The number of recordings to add to each chain.
            num_seeds_per_chain: The number of seeds to add to each chain.
        """
        game = Game(name=name)
        game.full_clean()
        game.save()

        for n in range(nchains):
            chain = Chain(game=game, name='chain {}'.format(n))
            chain.full_clean()
            chain.save()

            for seed_ix in range(num_seeds_per_chain):
                seed_file = File(open(self.path_to_test_audio(), 'rb'))
                seed_message = Message(chain=chain, audio=seed_file)
                seed_message.full_clean()
                seed_message.save()
                seed_file.close()

        def add_child(chain):
            parent = chain.pick_parent()
            with open(self.path_to_test_audio(), 'rb') as test_audio_handle:
                test_audio = File(test_audio_handle)
                child = Message(chain=chain, parent=parent, audio=test_audio)
                child.full_clean()
                child.save()
                parent.kill()

        for chain in game.chains.all():
            for _ in range(depth):
                add_child(chain)

    def create_survey(self, survey_name, from_game):
        game = Game.objects.get(name=from_game)
        chains = game.chains.all()

        questions = []
        choices = []

        for chain in chains:
            filled_messages = list(chain.messages.exclude(audio=''))
            choices.append(filled_messages[0].id)
            questions.append(filled_messages[-1].id)

        questions_str = ','.join(map(str, questions))
        choices_str = ','.join(map(str, choices))

        survey_form = NewSurveyForm({
            'name': survey_name,
            'num_questions_per_player': 10,
            'questions': questions_str,
            'choices': choices_str,
        })
        survey_form.full_clean()
        survey = survey_form.save()
        return survey

    def new_user(self):
        if self.browser:
            self.browser.quit()

        time.sleep(2)

        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(5)

    def nav_to_games_list(self):
        """The games list is the home page for the web app."""
        self.browser.get(self.live_server_url)

    def select_game_items(self):
        """Simply return the list elements corresponding to available games """
        game_list = self.browser.find_element_by_id('id_game_list')
        return game_list.find_elements_by_tag_name('li')

    def select_game_item_by_game_name(self, name):
        games = self.select_game_items()

        selected = None
        for game in games:
            if game.find_element_by_tag_name('h2').text.find(name) != -1:
                selected = game
                break

        return selected

    def play_game(self, name):
        game_list_item = self.select_game_item_by_game_name(name)
        game_list_item.find_element_by_class_name('play').click()

    def accept_instructions(self):
        """ Click accept on the instructions page """
        self.browser.find_element_by_id('accept').click()

    def simulate_sharing_mic(self):
        """ Execute the operations in micShared() """
        self.browser.execute_script("""
            telephoneView.audioRecorder = true;
        """)

    def path_to_test_audio(self):
        return Path(settings.APP_DIR, 'grunt/tests/media/test-audio.wav')

    def upload_file(self, recording=None):
        if not recording:
            recording = Path(settings.APP_DIR,
                             'grunt/tests/media/test-audio.wav')

        # Load a file blob to post via AJAX (hack!!)
        create_input_element = ('$( "<input>", {id: "tmpInput", type: "file"})'
                                '.appendTo("body");')
        self.browser.execute_script(create_input_element)

        # Give the file input a real file
        self.browser.find_element_by_id('tmpInput').send_keys(recording)

        """Take the file from the file input and post it.

        Hack!!! Create a global blob object to pass to the callback
        function manually, rather than creating it with the
        audioRecorder.

        Requires config to be a global object, and the callback
        function to accept a blob.
        """
        self.browser.execute_script('''
            blob = document.getElementById("tmpInput").files[0];
            $( "#tmpInput" ).remove();
            config.callback(blob);
        ''')

    def pass_mic_check(self):
        self.simulate_sharing_mic()
        self.upload_file()
        self.wait_for(tag='body')


    def wait_for(self, tag = None, id = None, text = None, timeout = 10):
        locator = (By.TAG_NAME, tag) if tag else (By.ID, id)

        if text:
            ec=expected_conditions.text_to_be_present_in_element(locator,text)
        else:
            ec=expected_conditions.presence_of_element_located(locator)

        WebDriverWait(self.browser, timeout).until(
            ec, 'Unable to find element {}'.format(locator))

    def assert_status(self, expected):
        status = self.browser.find_element_by_id('status').text
        self.assertEquals(status, expected)

    def assert_alert_message(self, expected):
        alert_message = self.browser.find_element_by_id('alert').text
        self.assertEquals(alert_message, expected)

    def assert_alert_message_contains(self, expected):
        alert_message = self.browser.find_element_by_id('alert').text
        self.assertRegexpMatches(alert_message, expected)

    def assert_completion_code_length(self, expected_length):
        completion_code = self.browser.\
            find_element_by_id('alert').\
            find_element_by_tag_name('code').\
            text
        parts = completion_code.split('-')
        self.assertEquals(len(parts), expected_length)

    def assert_error_message(self, expected):
        error_message = self.browser.find_element_by_id('message').text
        self.assertEquals(error_message, expected)

    def assert_completion_page(self):
        """ Assert the user made it to the completion page """
        title = self.browser.find_element_by_tag_name('h1').text
        self.assertEquals(title, 'Game Complete!')

    def assert_completion_code(self, expected):
        code = self.browser.find_element_by_tag_name('code').text
        self.assertEquals(code, expected)

    def assert_audio_src(self, expected):
        audio_src = self.browser.find_element_by_id('sound').get_attribute('src')
        self.assertRegexpMatches(audio_src, expected)

    # Inspect view

    def inspect_game(self, name):
        game_list_item = self.select_game_item_by_game_name(name)
        game_list_item.find_element_by_class_name('inspect').click()

    def select_svg_nodes(self):
        svg = self.browser.find_element_by_css_selector('svg.tree')
        return svg.find_elements_by_css_selector('g.node')

    def select_message_nodes(self):
        svg = self.browser.find_element_by_css_selector('svg.tree')
        return svg.find_elements_by_css_selector('g.node.message')

    def assert_filled_message(self, message_group):
        self.assertEquals(message_group.get_attribute('class'), 'message filled')

    def assert_empty_message(self, message_group):
        self.assertEquals(message_group.get_attribute('class'), 'message empty')

    def assert_chain_name(self, expected):
        """ Assert that a chain of the expected name is on the page

        On the inspect view, chains are shown one at a time. In order
        to tell which chain you are looking at, they are given a name
        at the top. This method asserts the name of that chain.
        """
        chain_name = self.browser.find_element_by_id('id_chain_name').text
        self.assertEquals(chain_name, expected)

    def select_survey_items(self):
        """ Select the survey list items from the survey list """
        survey_list = self.browser.find_element_by_id('id_survey_list')
        return survey_list.find_elements_by_tag_name('li')

    def select_survey_item_by_survey_name(self, name):
        """ Select a survey item by survey name """
        surveys = self.select_survey_items()

        selected = None
        for survey in surveys:
            if survey.find_element_by_tag_name('h2').text == name:
                selected = survey
                break

        return selected
