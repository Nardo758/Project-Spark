"""
OAuth Configuration for Google and GitHub
"""

import os
from typing import Dict, Any

# OAuth Provider Configurations
OAUTH_PROVIDERS = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "access_token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scopes": ["openid", "email", "profile"],
        "redirect_uri": None,  # Will be set dynamically
    },
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "authorize_url": "https://github.com/login/oauth/authorize",
        "access_token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "scopes": ["user:email"],
        "redirect_uri": None,  # Will be set dynamically
    },
    "linkedin": {
        "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
        "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET"),
        "authorize_url": "https://www.linkedin.com/oauth/v2/authorization",
        "access_token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "userinfo_url": "https://api.linkedin.com/v2/userinfo",
        "scopes": ["openid", "profile", "email"],
        "redirect_uri": None,  # Will be set dynamically
    }
}


def get_oauth_config(provider: str, redirect_uri: str) -> Dict[str, Any]:
    """
    Get OAuth configuration for a provider

    Args:
        provider: Provider name ('google' or 'github')
        redirect_uri: Callback URL for OAuth flow

    Returns:
        OAuth configuration dictionary
    """
    if provider not in OAUTH_PROVIDERS:
        raise ValueError(f"Unsupported OAuth provider: {provider}")

    config = OAUTH_PROVIDERS[provider].copy()
    config["redirect_uri"] = redirect_uri
    return config
