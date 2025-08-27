"""
Simple test runner to verify API functionality without external dependencies.
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))


async def test_basic_functionality():
    """Test basic API functionality."""
    try:
        # Test configuration loading
        from config import get_settings

        settings = get_settings()
        print(f"✅ Configuration loaded: {settings.app_name}")

        # Test database models import
        from models.companies import Company
        from models.drugs import Drug
        from models.users import User

        print("✅ Database models imported successfully")

        # Test authentication service
        from middleware.auth import AuthenticationService

        auth_service = AuthenticationService()

        # Test password hashing
        password = "test123"
        hashed = auth_service.get_password_hash(password)
        verified = auth_service.verify_password(password, hashed)
        assert verified, "Password verification failed"
        print("✅ Password hashing works correctly")

        # Test JWT token creation and verification
        token_data = {"sub": "test-user", "email": "test@example.com"}
        token = auth_service.create_access_token(token_data)
        decoded = await auth_service.verify_token(token)
        assert decoded is not None, "Token verification failed"
        assert decoded["sub"] == "test-user", "Token data incorrect"
        print("✅ JWT token creation and verification works")

        # Test route imports
        from routes import (
            auth,
            clinical_trials,
            companies,
            drugs,
            health,
            market,
            users,
        )

        print("✅ All route modules imported successfully")

        # Test main app creation
        from main import create_app

        app = create_app()
        print(f"✅ FastAPI app created successfully: {app.title}")

        print("\n🎉 All basic functionality tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_basic_functionality())
    sys.exit(0 if success else 1)
