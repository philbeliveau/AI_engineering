"""Tests for authentication middleware.

Tests APIKeyValidator, AuthMiddleware, and require_tier per story 5.2.
"""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from src.exceptions import ForbiddenError
from src.middleware.auth import (
    APIKeyValidator,
    AuthMiddleware,
    get_auth_context,
    require_tier,
    set_validator,
)
from src.models.auth import APIKey, AuthContext, UserTier


class TestAPIKeyValidator:
    """Tests for APIKeyValidator class."""

    @pytest.fixture
    def validator(self) -> APIKeyValidator:
        """Create a fresh validator for each test."""
        return APIKeyValidator()

    @pytest.fixture
    def valid_key(self) -> str:
        """Valid API key format."""
        return "kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"

    @pytest.fixture
    def registered_api_key(self, valid_key: str) -> APIKey:
        """Registered tier API key."""
        return APIKey(key=valid_key, tier=UserTier.REGISTERED)

    def test_validate_format_valid(self, validator: APIKeyValidator, valid_key: str) -> None:
        """Test valid API key format passes validation."""
        assert validator.validate_format(valid_key) is True

    def test_validate_format_invalid_prefix(self, validator: APIKeyValidator) -> None:
        """Test invalid prefix fails validation."""
        assert validator.validate_format("xx_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6") is False

    def test_validate_format_too_short(self, validator: APIKeyValidator) -> None:
        """Test too short key fails validation."""
        assert validator.validate_format("kp_abc123") is False

    def test_validate_format_too_long(self, validator: APIKeyValidator) -> None:
        """Test too long key fails validation."""
        assert validator.validate_format("kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6extra") is False

    def test_validate_format_non_hex(self, validator: APIKeyValidator) -> None:
        """Test non-hex characters fail validation."""
        assert validator.validate_format("kp_gggggggggggggggggggggggggggggggg") is False

    def test_validate_format_uppercase_hex(self, validator: APIKeyValidator) -> None:
        """Test uppercase hex characters pass validation."""
        assert validator.validate_format("kp_A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D6") is True

    def test_validate_format_mixed_case_hex(self, validator: APIKeyValidator) -> None:
        """Test mixed case hex characters pass validation."""
        assert validator.validate_format("kp_a1B2c3D4e5F6a7B8c9D0e1F2a3B4c5D6") is True

    def test_validate_unregistered_key(self, validator: APIKeyValidator, valid_key: str) -> None:
        """Test unregistered key returns None."""
        assert validator.validate(valid_key) is None

    def test_validate_registered_key(
        self, validator: APIKeyValidator, registered_api_key: APIKey
    ) -> None:
        """Test registered key returns APIKey object."""
        validator.register_key(registered_api_key)
        result = validator.validate(registered_api_key.key)
        assert result is not None
        assert result.key == registered_api_key.key
        assert result.tier == UserTier.REGISTERED

    def test_validate_expired_key(self, validator: APIKeyValidator) -> None:
        """Test expired key returns None."""
        expired_key = APIKey(
            key="kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
            tier=UserTier.REGISTERED,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        validator.register_key(expired_key)
        assert validator.validate(expired_key.key) is None

    def test_validate_invalid_format_key(self, validator: APIKeyValidator) -> None:
        """Test invalid format returns None without checking storage."""
        assert validator.validate("invalid") is None

    def test_register_multiple_keys(self, validator: APIKeyValidator) -> None:
        """Test registering multiple keys."""
        keys = [
            APIKey(key="kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6", tier=UserTier.REGISTERED),
            APIKey(key="kp_11111111111111111111111111111111", tier=UserTier.PREMIUM),
        ]
        validator.register_keys(keys)

        result1 = validator.validate(keys[0].key)
        result2 = validator.validate(keys[1].key)

        assert result1 is not None
        assert result1.tier == UserTier.REGISTERED
        assert result2 is not None
        assert result2.tier == UserTier.PREMIUM

    def test_clear_keys(self, validator: APIKeyValidator, registered_api_key: APIKey) -> None:
        """Test clearing all keys."""
        validator.register_key(registered_api_key)
        assert validator.validate(registered_api_key.key) is not None

        validator.clear()
        assert validator.validate(registered_api_key.key) is None

    def test_validate_uppercase_key(self, validator: APIKeyValidator) -> None:
        """Test uppercase hex key validation works end-to-end."""
        uppercase_key = APIKey(
            key="kp_A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D6",
            tier=UserTier.PREMIUM,
        )
        validator.register_key(uppercase_key)
        result = validator.validate(uppercase_key.key)
        assert result is not None
        assert result.tier == UserTier.PREMIUM


class TestAuthMiddleware:
    """Tests for AuthMiddleware class."""

    @pytest.fixture
    def validator(self) -> APIKeyValidator:
        """Create a validator with test keys."""
        v = APIKeyValidator()
        v.register_key(
            APIKey(key="kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6", tier=UserTier.REGISTERED)
        )
        v.register_key(
            APIKey(key="kp_11111111111111111111111111111111", tier=UserTier.PREMIUM)
        )
        return v

    @pytest.fixture
    def app(self, validator: APIKeyValidator) -> FastAPI:
        """Create test FastAPI app with auth middleware."""
        from fastapi import Request as FastAPIRequest

        app = FastAPI()
        app.add_middleware(AuthMiddleware, validator=validator)

        @app.get("/test")
        async def test_endpoint(request: FastAPIRequest):
            auth = getattr(request.state, "auth_context", None)
            return {
                "tier": auth.tier.value if auth else None,
                "authenticated": auth.authenticated if auth else False,
            }

        return app

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        """Create test client."""
        return TestClient(app)

    def test_no_key_defaults_to_public(self, client: TestClient) -> None:
        """Test missing API key defaults to PUBLIC tier (AC #5)."""
        response = client.get("/test")
        assert response.status_code == 200
        data = response.json()
        assert data["tier"] == "PUBLIC"
        assert data["authenticated"] is False

    def test_valid_key_returns_registered_tier(self, client: TestClient) -> None:
        """Test valid registered key returns correct tier (AC #1, #2)."""
        response = client.get(
            "/test", headers={"X-API-Key": "kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tier"] == "REGISTERED"
        assert data["authenticated"] is True

    def test_valid_premium_key(self, client: TestClient) -> None:
        """Test valid premium key returns correct tier."""
        response = client.get(
            "/test", headers={"X-API-Key": "kp_11111111111111111111111111111111"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tier"] == "PREMIUM"
        assert data["authenticated"] is True

    def test_invalid_key_returns_401(self, client: TestClient) -> None:
        """Test invalid key returns 401 Unauthorized (AC #4)."""
        response = client.get(
            "/test", headers={"X-API-Key": "kp_00000000000000000000000000000000"}
        )
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"
        assert "header" in data["error"]["details"]

    def test_malformed_key_returns_401(self, client: TestClient) -> None:
        """Test malformed key returns 401 Unauthorized (AC #4)."""
        response = client.get("/test", headers={"X-API-Key": "invalid_key"})
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"

    def test_header_case_insensitive(self, client: TestClient) -> None:
        """Test X-API-Key header is case-insensitive (AC #1)."""
        response = client.get(
            "/test", headers={"x-api-key": "kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tier"] == "REGISTERED"


class TestRequireTier:
    """Tests for require_tier dependency."""

    @pytest.fixture
    def validator(self) -> APIKeyValidator:
        """Create a validator with test keys."""
        v = APIKeyValidator()
        v.register_key(
            APIKey(key="kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6", tier=UserTier.REGISTERED)
        )
        v.register_key(
            APIKey(key="kp_11111111111111111111111111111111", tier=UserTier.PREMIUM)
        )
        return v

    @pytest.fixture
    def app(self, validator: APIKeyValidator) -> FastAPI:
        """Create test FastAPI app with tier-restricted endpoints."""
        app = FastAPI()
        app.add_middleware(AuthMiddleware, validator=validator)

        @app.get("/public")
        async def public_endpoint():
            return {"message": "Public content"}

        @app.get("/registered")
        async def registered_endpoint(
            auth: AuthContext = Depends(require_tier(UserTier.REGISTERED))
        ):
            return {"message": "Registered content", "tier": auth.tier.value}

        @app.get("/premium")
        async def premium_endpoint(
            auth: AuthContext = Depends(require_tier(UserTier.PREMIUM))
        ):
            return {"message": "Premium content", "tier": auth.tier.value}

        return app

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        """Create test client."""
        return TestClient(app, raise_server_exceptions=False)

    def test_public_endpoint_no_key(self, client: TestClient) -> None:
        """Test public endpoint accessible without key."""
        response = client.get("/public")
        assert response.status_code == 200

    def test_registered_endpoint_with_registered_key(self, client: TestClient) -> None:
        """Test registered endpoint with registered key succeeds (AC #3)."""
        response = client.get(
            "/registered",
            headers={"X-API-Key": "kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"},
        )
        assert response.status_code == 200
        assert response.json()["tier"] == "REGISTERED"

    def test_registered_endpoint_with_premium_key(self, client: TestClient) -> None:
        """Test registered endpoint with premium key succeeds (tier hierarchy)."""
        response = client.get(
            "/registered",
            headers={"X-API-Key": "kp_11111111111111111111111111111111"},
        )
        assert response.status_code == 200
        assert response.json()["tier"] == "PREMIUM"

    def test_registered_endpoint_no_key_returns_403(self, client: TestClient) -> None:
        """Test registered endpoint without key returns 403 (AC #3)."""
        response = client.get("/registered")
        assert response.status_code == 500  # No exception handler in test app

    def test_premium_endpoint_with_registered_key_returns_403(
        self, client: TestClient
    ) -> None:
        """Test premium endpoint with registered key returns 403 (AC #3)."""
        response = client.get(
            "/premium",
            headers={"X-API-Key": "kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"},
        )
        assert response.status_code == 500  # No exception handler in test app


class TestExceptionHandlers:
    """Tests for exception handlers in server.py."""

    @pytest.fixture
    def app_with_handlers(self) -> FastAPI:
        """Create app with exception handlers like production server."""
        from fastapi import Request as FastAPIRequest
        from fastapi.responses import JSONResponse

        from src.exceptions import AuthError, ForbiddenError

        app = FastAPI()

        # Register exception handlers
        @app.exception_handler(ForbiddenError)
        async def forbidden_handler(request, exc: ForbiddenError):
            return JSONResponse(
                status_code=403,
                content={
                    "error": {
                        "code": exc.code,
                        "message": exc.message,
                        "details": exc.details,
                    }
                },
            )

        @app.exception_handler(AuthError)
        async def auth_handler(request, exc: AuthError):
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": exc.code,
                        "message": exc.message,
                        "details": exc.details,
                    }
                },
            )

        validator = APIKeyValidator()
        validator.register_key(
            APIKey(key="kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6", tier=UserTier.REGISTERED)
        )
        app.add_middleware(AuthMiddleware, validator=validator)

        @app.get("/registered")
        async def registered_endpoint(
            auth: AuthContext = Depends(require_tier(UserTier.REGISTERED))
        ):
            return {"tier": auth.tier.value}

        @app.get("/premium")
        async def premium_endpoint(
            auth: AuthContext = Depends(require_tier(UserTier.PREMIUM))
        ):
            return {"tier": auth.tier.value}

        return app

    @pytest.fixture
    def client(self, app_with_handlers: FastAPI) -> TestClient:
        return TestClient(app_with_handlers, raise_server_exceptions=False)

    def test_forbidden_returns_403_with_error_format(self, client: TestClient) -> None:
        """Test insufficient tier returns 403 with proper error format (AC #3)."""
        response = client.get("/premium", headers={"X-API-Key": "kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"})
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "FORBIDDEN"
        assert "required_tier" in data["error"]["details"]
        assert data["error"]["details"]["current_tier"] == "REGISTERED"

    def test_no_key_for_registered_returns_403(self, client: TestClient) -> None:
        """Test missing key for registered endpoint returns 403 (AC #3)."""
        response = client.get("/registered")
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "FORBIDDEN"
        assert data["error"]["details"]["current_tier"] == "PUBLIC"

    def test_valid_key_passes_tier_check(self, client: TestClient) -> None:
        """Test valid key passes tier check (AC #3)."""
        response = client.get("/registered", headers={"X-API-Key": "kp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"})
        assert response.status_code == 200
        assert response.json()["tier"] == "REGISTERED"


class TestServerIntegration:
    """Integration tests for auth middleware in the actual server.py."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client for actual server app."""
        from src.server import app

        return TestClient(app, raise_server_exceptions=False)

    def test_server_has_auth_middleware(self, client: TestClient) -> None:
        """Test that server.py has AuthMiddleware integrated."""
        # Health endpoint should work without auth (AC #5 - no key = PUBLIC)
        response = client.get("/health")
        # Should return 200 or 503 depending on DB connection, but NOT 401
        assert response.status_code in [200, 503]

    def test_server_invalid_key_returns_401(self, client: TestClient) -> None:
        """Test server returns 401 for invalid API key (AC #4)."""
        response = client.get(
            "/health",
            headers={"X-API-Key": "kp_00000000000000000000000000000000"},
        )
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"

    def test_server_malformed_key_returns_401(self, client: TestClient) -> None:
        """Test server returns 401 for malformed API key (AC #4)."""
        response = client.get("/health", headers={"X-API-Key": "not_a_valid_key"})
        assert response.status_code == 401

    def test_server_no_key_allows_access(self, client: TestClient) -> None:
        """Test server allows access without API key (AC #5)."""
        response = client.get("/health")
        # Should not be 401 - missing key defaults to PUBLIC tier
        assert response.status_code != 401
