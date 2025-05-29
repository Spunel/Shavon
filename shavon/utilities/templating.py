import sanic

from types import ModuleType
from typing import Any, Callable
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from shavon.utilities import random_alphanumeric


def _build_env(
    template_path: str,
    config: dict[str, Any] = {},
    globals: dict[str, Callable] = {}
):

    # Build the template environment
    template_env = Environment(
        loader=FileSystemLoader(
            template_path, 
            encoding='utf-8'
        ), 
        **config
    )

    # Add globals
    for k, v in globals.items():
        template_env.globals[k] = v
    
    return template_env


def render_template(
    file_name: str,
    settings: ModuleType,
    request: sanic.request = None, 
    wrapper: str = 'public_wrapper.html',
    env_config: dict[str, Any] = {},
    **kwargs: dict[str, Any]
) -> str:
    """ Renders a template with given data and returns a string.
    """

    env = _build_env(
        settings.TEMPLATE_PATH, 
        config=env_config,
        globals={
            'len': len,
            'datetime': datetime,
            'nocache': random_alphanumeric,
            'str': str,
            'usd': lambda x: "${:,.2f} USD".format(x),
            'datefmt': lambda x: x.strftime('%Y-%m-%d'),
        }
    )
    
    template = env.get_template(file_name)

    context = dict(
        wrapper=wrapper,
        **settings.SAFE_SETTINGS,
    )

    if request:
        context['request'] = request
        if hasattr(request.ctx, 'notices'):
            context['notices'] = request.ctx.notices

    return template.render(context, **kwargs)

