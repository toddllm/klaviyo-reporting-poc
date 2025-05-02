import os
import pytest
import requests
import uuid
from unittest.mock import patch, MagicMock

# Import the functions to test
sys_path_patch = pytest.importorskip("sys").path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from seed_profiles import (
    random_email,
    random_profile,
    klaviyo_retry,
    post_json_api,
    create_and_subscribe_profiles
)


class TestRandomEmail:
    def test_random_email_no_prefix(self):
        """Test random_email without a prefix"""
        email = random_email("John", "Doe", 1)
        assert "@" in email
        assert email.startswith("john.doe")
        assert email.endswith(".com")

    def test_random_email_with_prefix_no_domain(self):
        """Test random_email with a prefix but no domain"""
        email = random_email("John", "Doe", 1, prefix="testuser")
        assert email == "testuser+1@example.com"

    def test_random_email_with_full_email_prefix(self):
        """Test random_email with a full email as prefix"""
        email = random_email("John", "Doe", 1, prefix="test@domain.com")
        assert email == "test+1@domain.com"


class TestRandomProfile:
    def test_random_profile_structure(self):
        """Test that random_profile returns the expected structure"""
        profile = random_profile(1)
        assert "email" in profile
        assert "first_name" in profile
        assert "last_name" in profile
        assert "properties" in profile
        assert "total_spent" in profile["properties"]
        assert "last_purchase_at" in profile["properties"]
        assert "favorite_category" in profile["properties"]

    def test_random_profile_with_prefix(self):
        """Test random_profile with a prefix"""
        profile = random_profile(1, prefix="test@example.com")
        assert profile["email"] == "test+1@example.com"


class TestKlaviyoRetry:
    @pytest.mark.parametrize("status_code", [200, 201, 202])
    def test_retry_decorator_success_2xx(self, status_code):
        """Test that the retry decorator returns the response for 200, 201, 202 status codes"""
        mock_response = MagicMock()
        mock_response.status_code = status_code

        @klaviyo_retry
        def mock_func():
            return mock_response

        result = mock_func()
        assert result == mock_response
        # raise_for_status should not be called for 200, 201, 202
        mock_response.raise_for_status.assert_not_called()
    
    def test_retry_decorator_other_2xx_success(self):
        """Test that the retry decorator returns the response for other 2xx status codes"""
        mock_response = MagicMock()
        mock_response.status_code = 204  # No Content
        mock_response.raise_for_status.return_value = None

        @klaviyo_retry
        def mock_func():
            return mock_response

        result = mock_func()
        assert result == mock_response
        # raise_for_status should be called for other 2xx
        mock_response.raise_for_status.assert_called_once()

    def test_retry_decorator_rate_limit(self):
        """Test that the retry decorator handles rate limits"""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {}

        # Create a proper HTTPError with a response attribute
        mock_error = requests.exceptions.HTTPError()
        mock_error.response = mock_response

        call_count = 0

        @klaviyo_retry
        def mock_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise mock_error
            return mock_response

        with patch('time.sleep'):
            result = mock_func()

        assert result == mock_response
        assert call_count == 2

    def test_retry_decorator_server_error(self):
        """Test that the retry decorator handles server errors"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.headers = {}

        # Create a proper HTTPError with a response attribute
        mock_error = requests.exceptions.HTTPError()
        mock_error.response = mock_response

        call_count = 0

        @klaviyo_retry
        def mock_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise mock_error
            return mock_response

        with patch('time.sleep'):
            result = mock_func()

        assert result == mock_response
        assert call_count == 2

    def test_retry_decorator_max_retries(self):
        """Test that the retry decorator raises an error after max retries"""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {}

        mock_error = requests.exceptions.HTTPError()
        mock_error.response = mock_response

        @klaviyo_retry
        def mock_func():
            raise mock_error

        with patch('time.sleep'), pytest.raises(RuntimeError, match="Max retries exceeded"):
            mock_func()


class TestPostJsonApi:
    def test_post_json_api_dry_run(self):
        """Test that post_json_api returns a mock response in dry run mode"""
        with patch('builtins.print') as mock_print:
            response = post_json_api("https://example.com", {"data": "test"}, dry_run=True)

        assert response.status_code == 200
        assert callable(response.json)
        assert callable(response.raise_for_status)
        mock_print.assert_called_once()

    @patch('requests.post')
    @patch('uuid.uuid4')
    def test_post_json_api_real_request(self, mock_uuid, mock_post):
        """Test that post_json_api makes a real request with proper headers"""
        mock_uuid.return_value = "test-uuid"
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        url = "https://example.com"
        payload = {"data": "test"}
        response = post_json_api(url, payload)

        assert response == mock_response
        mock_post.assert_called_once()
        
        # Check that the URL and payload are correct
        args, kwargs = mock_post.call_args
        assert args[0] == url
        assert kwargs['json'] == payload
        assert kwargs['timeout'] == 15
        
        # Check headers contain the expected values
        headers = kwargs['headers']
        assert "Klaviyo-API-Key" in headers['Authorization']
        assert headers['Content-Type'] == "application/json"
        assert headers['Accept'] == "application/json"
        assert headers['Idempotency-Key'] == "test-uuid"


class TestCreateAndSubscribeProfiles:
    @patch('seed_profiles.post_json_api')
    def test_create_and_subscribe_profiles_dry_run(self, mock_post_json_api):
        """Test create_and_subscribe_profiles in dry run mode"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post_json_api.return_value = mock_response
        
        profiles = [{"email": "test@example.com"}]
        emails, status_code = create_and_subscribe_profiles(profiles, dry_run=True)

        # Check return values
        assert emails == ["test@example.com"]
        assert status_code == 200
        
        mock_post_json_api.assert_called_once()
        args, kwargs = mock_post_json_api.call_args
        # Verify that dry_run was passed to post_json_api
        # The third positional argument should be True (dry_run)
        assert len(args) >= 3 and args[2] is True
        # Check the payload structure
        assert "data" in args[1]
        assert len(args[1]["data"]) == 1
        assert args[1]["data"][0]["type"] == "profile"
        assert args[1]["data"][0]["attributes"] == profiles[0]

    @pytest.mark.parametrize("status_code,status_msg", [
        (200, "updated"),
        (201, "created"),
        (202, "accepted for processing")
    ])
    @patch('seed_profiles.post_json_api')
    @patch('builtins.print')
    def test_create_and_subscribe_profiles_real_request(self, mock_print, mock_post_json_api, status_code, status_msg):
        """Test create_and_subscribe_profiles makes a real request and handles different status codes"""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_post_json_api.return_value = mock_response
        
        profiles = [{"email": "test@example.com"}]
        emails, returned_status_code = create_and_subscribe_profiles(profiles)

        # Check return values
        assert emails == ["test@example.com"]
        assert returned_status_code == status_code
        
        mock_post_json_api.assert_called_once()
        args, kwargs = mock_post_json_api.call_args
        # Verify that dry_run was not passed or is False
        assert 'dry_run' not in kwargs or kwargs['dry_run'] is False
        # Check the payload structure
        assert "data" in args[1]
        assert len(args[1]["data"]) == 1
        assert args[1]["data"][0]["type"] == "profile"
        assert args[1]["data"][0]["attributes"] == profiles[0]
        
        # Verify the print message contains the correct status message
        mock_print.assert_called_once()
        print_args = mock_print.call_args[0][0]
        assert status_msg in print_args.lower()
        assert str(status_code) in print_args


class TestMainFunction:
    @patch('seed_profiles.create_and_subscribe_profiles')
    @patch('seed_profiles.random_profile')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_function_with_prefix(self, mock_parse_args, mock_random_profile, mock_create_and_subscribe):
        """Test the main function with a prefix"""
        from seed_profiles import main

        # Mock the arguments
        mock_args = MagicMock()
        mock_args.prefix = "test@example.com"
        mock_args.num = 3
        mock_args.dry_run = True
        mock_parse_args.return_value = mock_args

        # Mock the profile generation
        mock_random_profile.side_effect = lambda i, prefix: {"email": f"test+{i}@example.com"}
        
        # Mock the create_and_subscribe_profiles return value
        mock_create_and_subscribe.return_value = ([f"test+{i}@example.com" for i in range(1, 4)], 201)

        # Run the main function
        with patch('builtins.print'):
            main()

        # Check that random_profile was called with the correct arguments
        assert mock_random_profile.call_count == 3
        for i in range(1, 4):
            mock_random_profile.assert_any_call(i, "test@example.com")

        # Check that create_and_subscribe_profiles was called with the correct arguments
        mock_create_and_subscribe.assert_called_once()
        args, kwargs = mock_create_and_subscribe.call_args
        assert len(args[0]) == 3
        # Verify that dry_run was passed correctly
        # The second positional argument should be True (dry_run)
        assert len(args) >= 2 and args[1] is True

    @patch('seed_profiles.create_and_subscribe_profiles')
    @patch('seed_profiles.random_profile')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_function_batch_processing(self, mock_parse_args, mock_random_profile, mock_create_and_subscribe):
        """Test that the main function processes profiles in batches"""
        from seed_profiles import main, BATCH_SIZE

        # Mock the arguments
        mock_args = MagicMock()
        mock_args.prefix = None
        mock_args.num = BATCH_SIZE + 10  # More than one batch
        mock_args.dry_run = False
        mock_parse_args.return_value = mock_args

        # Mock the profile generation
        mock_random_profile.side_effect = lambda i, prefix: {"email": f"test{i}@example.com"}
        
        # Mock the create_and_subscribe_profiles return value
        # First batch returns 201 (created), second batch returns 200 (updated)
        mock_create_and_subscribe.side_effect = [
            ([f"test{i}@example.com" for i in range(1, BATCH_SIZE + 1)], 201),
            ([f"test{i}@example.com" for i in range(BATCH_SIZE + 1, BATCH_SIZE + 11)], 200)
        ]

        # Run the main function
        with patch('builtins.print'):
            main()

        # Check that create_and_subscribe_profiles was called twice (for two batches)
        assert mock_create_and_subscribe.call_count == 2
        
        # First batch should have BATCH_SIZE profiles
        first_call_args = mock_create_and_subscribe.call_args_list[0][0][0]
        assert len(first_call_args) == BATCH_SIZE
        
        # Second batch should have the remaining profiles
        second_call_args = mock_create_and_subscribe.call_args_list[1][0][0]
        assert len(second_call_args) == 10
        
    def test_random_profile_with_ci_prefix(self):
        """Test that random_profile with 'ci' prefix yields deterministic emails"""
        profile = random_profile(1, prefix="ci")
        assert profile["email"] == "ci+1@example.com"
        
        profile = random_profile(42, prefix="ci")
        assert profile["email"] == "ci+42@example.com"
