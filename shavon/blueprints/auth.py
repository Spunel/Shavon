import jwt
import sanic

from pydantic import ValidationError
from sqlalchemy import select

from shavon import db
from shavon import settings
from shavon.models.auth import (
    User,
    LoginAttempt,
)
from shavon.models.session import Session
from shavon.utilities.session import (
    auth_required,
    clear_cookie
)
from shavon.utilities.templating import render_template
from shavon.utilities.json_helpers import (
    fail_response,
    ok_response
)
from shavon.validators.auth import LoginForm
from shavon.exceptions import ProcessingBreak

blueprint = sanic.Blueprint("auth", url_prefix="/auth")


@blueprint.route("/login", methods=["GET"], name="login")
async def login(request):
    """ Render the login page.
    """
    html_page = render_template(
        "auth/login.html", 
        settings=settings,
        request=request,
    )

    return sanic.response.html(html_page)


@blueprint.route("/login/proc", methods=["POST"], name="login_proc")
async def login_proc(request):
    """ Process the login form.
    """

    # Get/Create LoginAttempt record for the IP address
    async with db.session() as session:
        login_attempt = await LoginAttempt.get_attempt(
            session=session,
            ip_address=request.ip,
        )
        await session.flush()

        print(f"Login attempt for IP: {request.ip}, Current attempts: {login_attempt.attempt_count}")	
        # Increment the attempt count
        login_attempt.increment()
        session.add(login_attempt)
        await session.commit()

    generic_error = "Invalid credentials or account inactive."
    try:
        # Validate the form data
        require_captcha = bool(login_attempt.attempt_count > 3)
        print(f"Captcha required: {require_captcha}")
        auth_form = LoginForm(
            require_captcha=require_captcha,
            captcha=None,
            **request.json,
        )

        # TODO: Check captcha if required

        # Check credentials
        async with db.session() as session:
            email = auth_form.email.lower()
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user: User = result.scalars().first()
            if not user or not user.is_active:
                raise ProcessingBreak(generic_error)
            
            # Verify the password
            if not user.verify_password(
                hashed_password=user.password,
                pt_password=auth_form.password
            ):
                raise ProcessingBreak(generic_error)
                    
    except (ValidationError, ProcessingBreak) as e:
        # Handle validation errors or processing breaks
        return fail_response(message=str(e))
    
    except Exception as e:
        # Handle unexpected errors
        return fail_response(message="An unexpected error occurred: " + str(e))

    # Clear the login attempt record
    async with db.session() as session:
        await session.delete(login_attempt)
        await session.commit()

    # Create a new session record
    async with db.session() as session:
        user_session = await Session.create_session(
            session=session,
            user_id=user.id,
            ip_address=request.ip,
            user_agent=request.headers.get('user-agent', ''),
        )
        await session.commit()

    # Start with an ok_response
    response = ok_response()

    # Built the JWT payload with session key
    payload = { 
        "user_id": user.id,
        "session_key": user_session.session_key,
    }

    # Build the access_token
    access_token = jwt.encode(
        payload,
        settings.AUTH_COOKIE_SECRET_KEY,
        algorithm=settings.AUTH_COOKIE_ALGORITHM,
    )
    
    # Build the response and attach the cookie
    response = ok_response(
        redirect_url=request.app.url_for("profile.view", user_id=user.id)
    )
    response.add_cookie(
        settings.AUTH_COOKIE_NAME,
        access_token,
        domain=settings.AUTH_COOKIE_DOMAIN,
        max_age=settings.AUTH_COOKIE_LIFESPAN,
    )
    return response


@blueprint.route("/logout", methods=["GET"], name="logout")
@auth_required
async def logout(request):
    """ Log out the user by destroying their session.
    """

    # Delete the session from the database
    async with db.session() as session:
        # Get the session key from the cookie
        user_session = request.ctx.session
        
        # If a session exists, delete it
        if user_session:
            await session.delete(user_session)
            await session.commit()

    # Redirect to the login page
    response = sanic.response.redirect(
        request.app.url_for("auth.login")
    )

    # Clear the previous session cookie
    response = clear_cookie(response)

    return response