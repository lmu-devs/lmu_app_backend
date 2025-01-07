from unittest.mock import MagicMock, patch

import pytest

from api.src.v1.core.api_key import APIKey
from shared.src.core.exceptions import AuthenticationError, AuthorizationError
from shared.src.core.settings import get_settings


@pytest.fixture
def mock_db():
    db = MagicMock()
    return db

@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.ADMIN_API_KEY = "test_admin_key"
    settings.SYSTEM_API_KEY = "test_system_key"
    return settings

class TestAPIKey:
    @pytest.mark.asyncio
    async def test_verify_admin_api_key_success(self, mock_settings):
        with patch('api.src.v1.core.api_key.get_settings', return_value=mock_settings):
            result = await APIKey.verify_admin_api_key("test_admin_key")
            assert result is True

    @pytest.mark.asyncio
    async def test_verify_admin_api_key_failure(self, mock_settings):
        with patch('api.src.v1.core.api_key.get_settings', return_value=mock_settings):
            with pytest.raises(AuthenticationError):
                await APIKey.verify_admin_api_key("wrong_key")

    @pytest.mark.asyncio
    async def test_verify_system_api_key_success(self, mock_settings):
        with patch('api.src.v1.core.api_key.get_settings', return_value=mock_settings):
            result = await APIKey.verify_system_api_key("test_system_key")
            assert result is True

    @pytest.mark.asyncio
    async def test_verify_system_api_key_failure(self, mock_settings):
        with patch('api.src.v1.core.api_key.get_settings', return_value=mock_settings):
            with pytest.raises(AuthenticationError):
                await APIKey.verify_system_api_key("wrong_key")

    def test_generate_user_key_with_device_id(self, mock_settings):
        with patch('api.src.v1.core.api_key.get_settings', return_value=mock_settings):
            device_id = "test_device_123"
            key1 = APIKey.generate_user_key(device_id)
            key2 = APIKey.generate_user_key(device_id)
            # Same device_id should generate same key
            assert key1 == key2
            assert isinstance(key1, str)
            assert len(key1) > 0

    def test_generate_user_key_without_device_id(self):
        key1 = APIKey.generate_user_key(None)
        key2 = APIKey.generate_user_key(None)
        # Random keys should be different
        assert key1 != key2
        assert isinstance(key1, str)
        assert len(key1) > 0

    @pytest.mark.asyncio
    async def test_verify_user_api_key_success(self, mock_db):
        mock_user = MagicMock()
        mock_user.id = "test_user_id"
        mock_db.query().filter().first.return_value = mock_user
        
        result = await APIKey.verify_user_api_key("test_user_key", mock_db)
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_verify_user_api_key_failure(self, mock_db):
        mock_db.query().filter().first.return_value = None
        
        with pytest.raises(AuthorizationError):
            await APIKey.verify_user_api_key("invalid_key", mock_db)

    @pytest.mark.asyncio
    async def test_verify_user_api_key_soft_with_user(self, mock_db):
        mock_user = MagicMock()
        mock_user.id = "test_user_id"
        mock_db.query().filter().first.return_value = mock_user
        
        result = await APIKey.verify_user_api_key_soft("test_user_key", mock_db)
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_verify_user_api_key_soft_without_user(self, mock_db):
        mock_db.query().filter().first.return_value = None
        
        result = await APIKey.verify_user_api_key_soft("invalid_key", mock_db)
        assert result is None
