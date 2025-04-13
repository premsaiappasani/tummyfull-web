import os
import importlib

def register_blueprints(app):
    controllers_dir = os.path.dirname(__file__)
    for filename in os.listdir(controllers_dir):
        if filename.endswith('_controller.py'):
            module_name = filename[:-3]  # Remove '.py'
            module = importlib.import_module(f'.{module_name}', package='app.controllers')
            if hasattr(module, 'get_blueprint'):
                blueprint = module.get_blueprint()
                app.register_blueprint(blueprint)