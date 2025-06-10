import functools
import jwt

from sanic import response
from sanic.request import Request

from shavon import db
from shavon import settings
from shavon.models.auth import User
from shavon.models.session import Session


def auth_required(func):
    """
    Decorator to wrap protected blueprint routes and check if the user's session is valid.
    If the session is invalid, destroy the cookie and redirect to the login page.
    """
    @functools.wraps(func)
    async def wrapper(request, *args, **kwargs):
        # Get the auth cookie
        auth_cookie = request.cookies.get(settings.AUTH_COOKIE_NAME)
        if not auth_cookie:
            return response.redirect(request.app.url_for('auth.login'))
        
        try:
            # Decode the JWT payload
            payload = jwt.decode(
                auth_cookie,
                settings.AUTH_COOKIE_SECRET_KEY,
                algorithms=[settings.AUTH_COOKIE_ALGORITHM],
            )
            
            # Extract user_id and session_key from payload
            user_id = payload.get('user_id')
            session_key = payload.get('session_key')
            
            if not user_id or not session_key:
                raise jwt.InvalidTokenError("Missing user_id or session_key in payload")
            
            # Verify the session exists and is valid
            async with db.session() as session:
                user_session = await Session.get_by_user_and_key(
                    session=session,
                    user_id=user_id,
                    session_key=session_key
                )
                
                if not user_session:
                    raise jwt.InvalidTokenError("Invalid session")
                
                # Get the user data
                user = await User.get_by_id(session=session, user_id=user_id)
                if not user or not user.is_active:
                    raise jwt.InvalidTokenError("User not found or inactive")
                
                # Update last_accessed timestamp
                await user_session.update_last_accessed(session)
                await session.commit()
                
                # Attach user to request for use in the view function
                request.ctx.user = user
                request.ctx.session = user_session
                
        except jwt.InvalidTokenError:
            # If session is invalid, destroy the cookie and redirect to login
            redirect = response.redirect(
                request.app.url_for('auth.login')
            )
            redirect = clear_cookie(redirect)
            return redirect
        
        # Continue with the original route function
        return await func(request, *args, **kwargs)
    
    return wrapper


def clear_cookie(response: response.HTTPResponse) -> response.HTTPResponse:
    """
    Clear the session cookie by setting its max_age to 0.
    This is used when the session is invalid or when logging out.
    """

    # Clear the session cookie
    response.add_cookie(
        settings.AUTH_COOKIE_NAME,
        '',
        domain=settings.AUTH_COOKIE_DOMAIN,
        max_age=0,  # Set max_age to 0 to delete the cookie
    )
    
    return response

