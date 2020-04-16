import uuid
from flask import Blueprint
from flask import Flask, json, Response, request, abort
from flask import jsonify, make_response

# Add new blueprints here
if __package__ is None or __package__ == '':
    # uses current directory visibility
    import product_table_client
    from custom_logger import setup_logger
else:
    # uses current package visibility
    from flaskr import product_table_client
    from flaskr.custom_logger import setup_logger

# Set up the custom logger and the Blueprint
logger = setup_logger(__name__)
product_module = Blueprint('products', __name__)

logger.info("Intialized product routes")

# Allow the default route to return a health check
@product_module.route('/')
def health_check():
    return "This a health check. Product Management Service is up and running."

# Get all products
@product_module.route('/products')
def get_all_products():
    try:
        service_response = product_table_client.get_all_products()
    except Exception as e:
        logger.error(e)
        abort(400)
    resp = Response(service_response)
    resp.headers["Content-Type"] = "application/json"
    return resp

# Get product by productId
@product_module.route("/products/<string:productId>", methods=['GET'])
def get_product(productId):
    try:
        service_response = product_table_client.get_product(productId)
    except Exception as e:
        logger.error(e)
        abort(400)
    resp = Response(service_response)
    resp.headers["Content-Type"] = "application/json"
    return resp

# Add a new product
@product_module.route("/products", methods=['POST'])
def create_product():
    try:
        product_dict = json.loads(request.data)
        service_response = product_table_client.create_product(product_dict)
    except Exception as e:
        logger.error(e)
        abort(400)        
    resp = Response(service_response, 201)
    resp.headers["Content-Type"] = "application/json"
    return resp

# Update product by productId
@product_module.route("/products/<productId>", methods=['PUT'])
def update_product(productId):
    try:
        product_dict = json.loads(request.data)
        service_response = product_table_client.update_product(productId, product_dict)
    except Exception as e:
        logger.error(e)
        abort(400)
    resp = Response(service_response, 200)
    resp.headers["Content-Type"] = "application/json"
    return resp

# Delete product by productId
@product_module.route("/products/<productId>", methods=['DELETE'])
def delete_product(productId):
    try:
        service_response = product_table_client.delete_product(productId)
    except Exception as e:
        logger.error(e)
        abort(400)
    resp = Response(service_response, 200)
    resp.headers["Content-Type"] = "application/json"
    return resp

@product_module.errorhandler(400)
def bad_request(e):
    logger.error(e)
    # note that we set the 400 status explicitly
    errorResponse = json.dumps({'error': 'Bad request'})
    resp = Response(errorResponse, 400)
    resp.headers["Content-Type"] = "application/json"
    return resp