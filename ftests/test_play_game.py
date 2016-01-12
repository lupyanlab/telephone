from unittest import skip
from unipath import Path
from django.conf import settings
from .base import FunctionalTest


class TelephoneTest(FunctionalTest):
    """Test basic telephone game functionality."""
    def test_respond_to_seed_message(self):
        """Lynn plays a round of the telephone game."""
        game_name = 'Fresh Game'
        self.create_game(name=game_name)

        # She navigates to the site and sees the game.
        self.nav_to_games_list()
        available_games = self.select_game_items()
        self.assertEquals(len(available_games), 1)

        # She decides to play the game.
        self.play_game(game_name)

        # She agrees to participate.
        self.accept_instructions()

        # She shares her microphone.
        self.simulate_sharing_mic()

        # She plays the sound.
        self.browser.find_element_by_id('listen').click()
        speaker_img = self.browser.find_element_by_id('listen')
        self.assertIn('button-on', speaker_img.get_attribute('class'))

        # She records an entry.
        self.upload_file()
        self.wait_for(tag = 'body')

        # She sees that her entry was successful.
        self.assert_alert_message_contains("Your completion code is")
        self.assert_completion_code_length(1)

    def test_respond_to_multiple_chains(self):
        """Lynn makes two recordings in a game with two chains."""
        game_name = 'Two Chain Game'
        self.create_game(name=game_name, nchains=2)

        # She navigates to the game page and plays the game.
        self.nav_to_games_list()
        self.play_game(game_name)

        # She gets her browser ready to play.
        self.accept_instructions()
        self.simulate_sharing_mic()

        # She plays the sound and makes her response.
        self.upload_file()
        self.wait_for(tag = 'body')

        # She sees that her recording was successful.
        self.assert_alert_message_contains('Your message was received!')

        # She plays the second sound and makes her response.
        self.upload_file()
        self.wait_for(tag = 'body')

        # Her entry was successful
        self.assert_alert_message_contains("Your completion code is")
        self.assert_completion_code_length(2)

    def test_player_with_quiet_submission_has_to_resubmit(self):
        """Marcus makes a submission that's too quiet."""
        game_name = 'Quiet Game'
        self.create_game(game_name, nchains=1)

        # Marcus navigates to the game page and plays the Game
        self.nav_to_games_list()
        self.play_game(game_name)

        # He accepts the instructions and shares his microphone.
        self.accept_instructions()
        self.simulate_sharing_mic()

        # He creates a recording that's too quiet.
        quiet_recording = Path(
            settings.APP_DIR,
            'grunt/tests/media/crow_40.wav'
        )
        self.upload_file(quiet_recording)
        self.wait_for(tag='body')

        # He sees an alert message that says his recording was too quiet
        self.assert_alert_message_contains("Your recording wasn't loud enough")

        # He tries again and this time he passes.
        self.upload_file()
        self.wait_for(tag='body')
        self.assert_alert_message_contains("Your completion code is")
        self.assert_completion_code_length(1)

    @skip("Getting a broken pipe error when submitting a second time")
    def test_session_is_cleared_on_completion_page(self):
        """Marcus plays the same game twice."""
        game_name = 'Short game'
        self.create_game(game_name, nchains=1)

        # He navigates to the game page and plays the game.
        self.nav_to_games_list()
        self.play_game(game_name)

        # He accepts the instructions and gives his browser permission
        # to use the microphone.
        self.accept_instructions()
        self.simulate_sharing_mic()

        # He makes a recording.
        self.upload_file()
        self.wait_for(tag='body')

        # He lands on the completion page after making his 1 entry.
        self.assert_alert_message_contains("Your completion code is")
        self.assert_completion_code_length(1)

        # He navigates back to the game list to play the game again.
        self.nav_to_games_list()
        self.play_game(game_name)

        # He's back at the player page without seeing the instructions page.
        title = self.browser.find_element_by_tag_name('h1').text
        self.assertEquals(title, 'Telephone Game')

        # He shares his mic again and makes another entry.
        self.simulate_sharing_mic()
        self.upload_file()
        self.wait_for(tag='body')

        # He lands back at the completion page for a second time.
        self.assert_alert_message_contains("Your completion code is")
        self.assert_completion_code_length(1)


class ParallelBranchTest(FunctionalTest):
    def get_current_audio_url(self):
        return self.browser.execute_script('return message.get("audio");')

    def test_parallel_branches(self):
        """Marcus and Lynn respond to different seeds in the same chain."""
        game_name = 'Parallel Game'
        self.create_game(name=game_name) # TODO: add num_seeds_per_chain kwarg

        # Lynn gets set up to play the game
        self.nav_to_games_list()
        self.play_game(game_name)
        self.accept_instructions()
        self.simulate_sharing_mic()

        # Save the url of the first seed
        first_seed = self.get_current_audio_url()
        self.assertRegexpMatches(first_seed, 'seed', 'message was not a seed')

        # Lynn makes her response and leaves
        self.upload_file()
        self.wait_for(tag='body')
        self.assert_alert_message_contains("Your completion code is")

        # Marcus arrives
        self.new_user()
        self.nav_to_games_list()
        self.play_game(game_name)
        self.accept_instructions()
        self.simulate_sharing_mic()

        # Marcus does not hear the same seed that Lynn heard
        second_seed = self.get_current_audio_url()
        self.assertRegexpMatches(second_seed, 'seed', 'message was not a seed')
        self.assertNotEqual(first_seed, second_seed)

        # Marcus makes his recording and leaves
        self.upload_file()
        self.wait_for(tag='body')
        self.assert_alert_message_contains("Your completion code is")


class InterfaceTest(FunctionalTest):
    def setUp(self):
        super(InterfaceTest, self).setUp()

        # Create a game and navigate to the player,
        # accepting instructions on the way.
        game_name = 'Basic Game'
        self.create_game(name=game_name)
        self.nav_to_games_list()
        self.play_game(game_name)
        self.accept_instructions()

    def test_share_mic_before_listening(self):
        """Lynn has to share her mic before she can listen to the recording."""
        # The recorder isn't available because she hasn't shared her
        # microphone yet.
        recorder = self.browser.find_element_by_id('record')
        self.assertIn('unavailable', recorder.get_attribute('class'))

        # When she clicks on it, she gets a message telling her how to start.
        recorder.click()
        self.assert_alert_message("Click on the telephone to start.")

        # She can't play the recording yet either.
        self.browser.find_element_by_id('listen').click()
        self.assert_alert_message("Click on the telephone to start.")

        # She shares her microphone but she still can't record a sound.
        self.simulate_sharing_mic()
        recorder.click()
        self.assert_alert_message("You have to listen to the message first.")
