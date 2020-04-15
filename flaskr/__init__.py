#!/usr/bin/env python
import os

from flask import Flask
from flask_cors import CORS

# Import the X-Ray modules
from aws_xray_sdk.core import xray_recorder, patch_all
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

# Add new blueprints here
if __package__ is None or __package__ == '':
    # uses current directory visibility
		from product_routes import product_module
else:
    # uses current package visibility
    from flaskr.product_routes import product_module

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	CORS(app)

	# AWS X-Ray
	plugins = ('EC2Plugin', 'ECSPlugin')
	xray_recorder.configure(service='myproject-product-service',plugins=plugins)
	XRayMiddleware(app, xray_recorder)
	patch_all()

	app.config.from_mapping(
		SECRET_KEY="dev",
		DATABASE="sample://db-string"
	)

	if test_config is None:
		# load the instance config, if it exists, when not testing
		app.config.from_pyfile("config.py", silent=True)
	else:
		# load the test config if passed in
		app.config.update(test_config)

	# ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# Add a blueprint for the products module
	app.register_blueprint(product_module)
	
	return app