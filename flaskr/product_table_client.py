import boto3
import json
import logging
from collections import defaultdict
import argparse
import uuid

import datetime
from datetime import date

from boto3.dynamodb.conditions import Key, Attr
if __package__ is None or __package__ == '':
	# uses current directory visibility
	from custom_logger import setup_logger
	from db import get_db_resource
else:
	# uses current package visibility
	from flaskr.custom_logger import setup_logger
	from flaskr.db import get_db_resource

logger = setup_logger(__name__)
table_name = 'products'

def get_all_products():
	dynamodb = get_db_resource()
	table = dynamodb.Table(table_name)
	response = table.scan(
			Select='ALL_ATTRIBUTES'
	)
	# logger.info("Logger Response: ")
	# logger.info(response)    
	product_list = defaultdict(list)

	for item in response["Items"]:
		product = {
			'productId': item['productId'],
			'currency': item['currency'],
			'interestPaymentPeriod': item['interestPaymentPeriod'],
			'interestPaymentDate': item['interestPaymentDate'],
			'rate': item['rate'],
			'productDescription': item['productDescription'],
			'createdDate': item['createdDate'],
			'updatedDate': item['updatedDate'],
			'imageUrl': item['imageUrl'],
		}
		product_list["products"].append(product)
	return json.dumps(product_list)

def get_product(productId):
	dynamodb = get_db_resource()
	table = dynamodb.Table(table_name)
	response = table.get_item(
		Key={
			'productId': productId
		}
	)
	# logger.info("Logger Response: ")
	# logger.info(response)
	if 'Item' not in response:
		return json.dumps({'error': 'Product does not exist'})

	item = response['Item']

	product = {
		'productId': item['productId'],
		'currency': item['currency'],
		'interestPaymentPeriod': item['interestPaymentPeriod'],
		'interestPaymentDate': item['interestPaymentDate'],
		'rate': item['rate'],
		'productDescription': item['productDescription'],
		'createdDate': item['createdDate'],
		'updatedDate': item['updatedDate'],
		'imageUrl': item['imageUrl'],
	}
	return json.dumps({'product': product})

def create_product(product_dict):
	productId = product_id_generator() # str(uuid.uuid4())
	currency = str(product_dict['currency'])
	interestPaymentPeriod = str(product_dict['interestPaymentPeriod'])
	interestPaymentDate = str(product_dict['interestPaymentDate'])
	rate = str(product_dict['rate'])
	productDescription = str(product_dict['productDescription'])
	createdDate = str(datetime.datetime.now().isoformat())
	updatedDate = "1900-01-01T00:00:00.000000"
	imageUrl = str(product_dict['imageUrl'])

	dynamodb = get_db_resource()
	table = dynamodb.Table(table_name)
	response = table.put_item(
		TableName=table_name,
		Item={
				'productId': productId,
				'currency':  currency,
				'interestPaymentPeriod': interestPaymentPeriod,
				'interestPaymentDate': interestPaymentDate,
				'rate': rate,
				'productDescription': productDescription,
				'createdDate': createdDate,
				'updatedDate': updatedDate,
				'imageUrl': imageUrl
			}
		)
	# logger.info("Logger Response: ")
	# logger.info(response)
	product = {
		'productId': productId,
		'currency': currency,
		'interestPaymentPeriod': interestPaymentPeriod,
		'interestPaymentDate': interestPaymentDate,
		'rate': rate,
		'productDescription': productDescription,
		'createdDate': createdDate,
		'updatedDate': updatedDate,
		'imageUrl': imageUrl,
	}
	return json.dumps({'product': product})

def update_product(productId, product_dict):
	currency = str(product_dict['currency'])
	interestPaymentPeriod = str(product_dict['interestPaymentPeriod'])
	interestPaymentDate = str(product_dict['interestPaymentDate'])
	rate = str(product_dict['rate'])
	productDescription = str(product_dict['productDescription'])
	updatedDate = str(datetime.datetime.now().isoformat())
	imageUrl = str(product_dict['imageUrl'])

	dynamodb = get_db_resource()
	table = dynamodb.Table(table_name)
	response = table.update_item(
		Key={
			'productId': productId
		},
		UpdateExpression="""SET currency = :p_currency,
								interestPaymentPeriod = :p_interestPaymentPeriod,
								interestPaymentDate = :p_interestPaymentDate,
								rate = :p_rate,
								productDescription = :p_productDescription,
								updatedDate = :p_updatedDate,
								imageUrl = :p_imageUrl
								""",
		ExpressionAttributeValues={
			':p_currency': currency,
			':p_interestPaymentPeriod' : interestPaymentPeriod,
			':p_interestPaymentDate':  interestPaymentDate,
			':p_rate': rate,
			':p_productDescription': birtproductDescriptionhDate,
			':p_updatedDate':  updatedDate,
			':p_imageUrl':  imageUrl
		},
		ReturnValues="ALL_NEW"
	)
	logger.info("Logger Response: ")
	logger.info(response)

	if 'Item' not in response:
		return json.dumps({'error': 'Product does not exist'})

	updated = response['Attributes']
	product = {
		'productId': updated['productId'],
		'currency': updated['currency'],
		'interestPaymentPeriod': updated['interestPaymentPeriod'],
		'interestPaymentDate': updated['interestPaymentDate'],
		'rate': updated['rate'],
		'productDescription': updated['productDescription'],
		'createdDate': updated['createdDate'],
		'updatedDate': updated['updatedDate'],
		'imageUrl': updated['imageUrl'],
	}
	return json.dumps({'product': product})

def delete_product(productId):
	dynamodb = get_db_resource()
	table = dynamodb.Table(table_name)
	response = table.delete_item(
		TableName=table_name,
		Key={
			'productId': productId
		}
	)

	logger.info("Logger Response: ")
	logger.info(response)

	if 'Item' not in response:
		return json.dumps({'error': 'product does not exist'})

	product = {
		'productId' : productId,
	}
	return json.dumps({'product': product})

def get_max_value(attribute):
	"""Will scan the table for the maximum possible value given an attribute"""
	maximum = None
	dynamodb = get_db_resource()
	table = dynamodb.Table(table_name)
	response = table.scan(
		Select='SPECIFIC_ATTRIBUTES',
	 	AttributesToGet=[
	 		attribute
	  ],
		ConsistentRead=True,
	)

	if response['Items'] == []: 
		pass
	else: 
		maximum = max([int(m[attribute]) for m in response['Items']])
	return maximum

def product_id_generator():
	now = datetime.datetime.now()
	max_value = get_max_value('productId')

	if max_value: 
		# get latest id from db and increment
		# get last 4 digits
		last_digits = str(max_value)[-4:]
		logger.info("last digits")
		logger.info(last_digits)
		new_product_id = 'VBCA' +  str(int(last_digits) + 1).zfill(4)
	else: 
		new_product_id = 'VBCA' + '0001'
	return new_product_id