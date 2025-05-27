import sanic

from shavon import settings
from shavon.utilities.templating import render_template


blueprint = sanic.Blueprint("info", url_prefix="/")

@blueprint.route("/", methods=["GET"])
async def index(request):
    """
    Render the index page.
    """
    response = sanic.response.html(
        render_template(
            "info/index.html", 
            settings=settings,
            request=request
        )
    )
    return response
