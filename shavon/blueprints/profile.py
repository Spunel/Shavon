import sanic
from sanic.exceptions import NotFound

from shavon import db
from shavon import settings
from shavon.models.auth import User 
from shavon.utilities.templating import render_template


blueprint = sanic.Blueprint("profile", url_prefix="/profile")

@blueprint.route("/manage", methods=["GET"], name="manage")
async def profile_manage(request):
    """
    Render the manage profile page.
    """
    response = sanic.response.html(
        render_template(
            "profile/manage.html", 
            settings=settings,
            request=request
        )
    )
    return response

@blueprint.route("/view/<user_id:int>", methods=["GET"], name="view")
async def profile_view(request, user_id: int):
    """
    Render the view profile page for a specific user.
    """
    async with db.session() as session:
        # Fetch user details from the database
        user = await User.get_by_id(session=session, user_id=user_id)
        if not user:
            raise NotFound(f"Could not find user.")
        
    response = sanic.response.html(
        render_template(
            "profile/view.html", 
            settings=settings,
            request=request,
            user=user
        )
    )
    return response