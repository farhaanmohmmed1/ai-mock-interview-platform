import pytest
from backend.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)


def test_password_hashing():
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_access_token():
    """Test JWT token creation and decoding"""
    data = {"sub": 1, "username": "testuser"}
    token = create_access_token(data)
    
    assert token is not None
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == 1
    assert decoded["username"] == "testuser"


def test_invalid_token():
    """Test invalid token decoding"""
    invalid_token = "invalid.token.here"
    decoded = decode_access_token(invalid_token)
    
    assert decoded is None
