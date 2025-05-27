import sanic
import importlib

from shavon import settings

# Create a Sanic app instance
app = sanic.Sanic(settings.APP_NAME)

# Attach Static directory for serving static files
app.static('/static', './static')

# Attach Blueprints
for module_name, bp_name in settings.BLUEPRINTS_ENABLED:
    try:
        loaded_module = importlib.import_module(module_name)
        loaded_bp = getattr(loaded_module, bp_name, None)
        if not loaded_bp:
            raise ImportError(f"Blueprint {module_name}.{bp_name} not found.")
        
        # Register the blueprint with the app
        app.blueprint(loaded_bp)
        # TODO: This should be logged to output log

    except (ImportError, ModuleNotFoundError) as err:
        # TODO: This should be logged to error log
        raise err
    
# Run the server
if __name__ == "__main__":
    app.run(
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        debug=settings.APP_DEBUG,
    )

