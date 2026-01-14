"""
OAuth Service for Google and GitHub Authentication
"""

import httpx
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlencode
import secrets

from app.core.oauth_config import get_oauth_config


class OAuthService:
    """Service for handling OAuth authentication flows"""

    @staticmethod
    def generate_state() -> str:
        """Generate a random state token for CSRF protection"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def get_authorization_url(provider: str, redirect_uri: str, state: str) -> str:
        """
        Generate OAuth authorization URL

        Args:
            provider: OAuth provider ('google' or 'github')
            redirect_uri: Callback URL
            state: CSRF protection token

        Returns:
            Authorization URL to redirect user to
        """
        config = get_oauth_config(provider, redirect_uri)
        if not config.get("client_id"):
            raise ValueError(f"{provider} OAuth not configured (missing client_id)")

        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(config["scopes"]),
            "state": state,
        }

        # GitHub uses comma-separated scopes
        if provider == "github":
            params["scope"] = ",".join(config["scopes"])

        return f"{config['authorize_url']}?{urlencode(params)}"

    @staticmethod
    async def exchange_code_for_token(
        provider: str,
        code: str,
        redirect_uri: str
    ) -> Optional[str]:
        """
        Exchange authorization code for access token

        Args:
            provider: OAuth provider
            code: Authorization code from callback
            redirect_uri: Same redirect URI used in authorization

        Returns:
            Access token or None if exchange fails
        """
        config = get_oauth_config(provider, redirect_uri)
        if not config.get("client_id") or not config.get("client_secret"):
            raise ValueError(f"{provider} OAuth not configured (missing client_id/client_secret)")

        data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    config["access_token_url"],
                    data=data,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                token_data = response.json()
                return token_data.get("access_token")
            except Exception as e:
                # Best-effort logging without leaking secrets.
                try:
                    status = response.status_code  # type: ignore[name-defined]
                    body = response.text  # type: ignore[name-defined]
                    print(f"Token exchange error for {provider}: HTTP {status} {body}")
                except Exception:
                    print(f"Token exchange error for {provider}: {e}")
                return None

    @staticmethod
    async def get_user_info(
        provider: str,
        access_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch user information from OAuth provider

        Args:
            provider: OAuth provider
            access_token: Access token from provider

        Returns:
            User info dict or None if fetch fails
        """
        config = get_oauth_config(provider, "")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    config["userinfo_url"],
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                user_data = response.json()

                # Normalize user data across providers
                return OAuthService._normalize_user_data(provider, user_data)
            except Exception as e:
                try:
                    status = response.status_code  # type: ignore[name-defined]
                    body = response.text  # type: ignore[name-defined]
                    print(f"User info fetch error for {provider}: HTTP {status} {body}")
                except Exception:
                    print(f"User info fetch error for {provider}: {e}")
                return None

    @staticmethod
    async def get_user_email_github(access_token: str) -> Optional[str]:
        """
        Fetch primary email from GitHub (separate endpoint)

        Args:
            access_token: GitHub access token

        Returns:
            Primary email or None
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.github.com/user/emails",
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                emails = response.json()

                # Find primary verified email
                for email in emails:
                    if email.get("primary") and email.get("verified"):
                        return email.get("email")

                # Fallback to first verified email
                for email in emails:
                    if email.get("verified"):
                        return email.get("email")

                return None
            except Exception as e:
                print(f"GitHub email fetch error: {e}")
                return None

    @staticmethod
    def _normalize_user_data(provider: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize user data across different OAuth providers

        Args:
            provider: OAuth provider name
            raw_data: Raw user data from provider

        Returns:
            Normalized user data dictionary
        """
        if provider == "google":
            return {
                "provider": "google",
                "provider_user_id": raw_data.get("id"),
                "email": raw_data.get("email"),
                "name": raw_data.get("name"),
                "avatar_url": raw_data.get("picture"),
                "email_verified": raw_data.get("verified_email", False),
            }
        elif provider == "github":
            return {
                "provider": "github",
                "provider_user_id": str(raw_data.get("id")),
                "email": raw_data.get("email"),  # May be None, needs separate fetch
                "name": raw_data.get("name") or raw_data.get("login"),
                "avatar_url": raw_data.get("avatar_url"),
                "email_verified": True,  # GitHub emails are always verified
            }
        elif provider == "linkedin":
            return {
                "provider": "linkedin",
                "provider_user_id": raw_data.get("sub"),
                "email": raw_data.get("email"),
                "name": raw_data.get("name"),
                "avatar_url": raw_data.get("picture"),
                "email_verified": raw_data.get("email_verified", False),
            }
        else:
            return {}

    @staticmethod
    async def complete_oauth_flow(
        provider: str,
        code: str,
        redirect_uri: str
    ) -> Optional[Dict[str, Any]]:
        """
        Complete full OAuth flow: exchange code and fetch user info

        Args:
            provider: OAuth provider
            code: Authorization code
            redirect_uri: Redirect URI

        Returns:
            Normalized user info or None if flow fails
        """
        # Exchange code for token
        access_token = await OAuthService.exchange_code_for_token(
            provider, code, redirect_uri
        )

        if not access_token:
            return None

        # Get user info
        user_info = await OAuthService.get_user_info(provider, access_token)

        if not user_info:
            return None

        # For GitHub, fetch email separately if not included
        if provider == "github" and not user_info.get("email"):
            email = await OAuthService.get_user_email_github(access_token)
            user_info["email"] = email

        return user_info


oauth_service = OAuthService()
