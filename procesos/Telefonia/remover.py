####################################################################################################
##                                 ELIMINAR ARCHIVOS DEL STORAGE                                  ##
####################################################################################################


########################### LIBRERIAS #####################################
from flask import Blueprint
from flask import jsonify
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from google.cloud import datastore
from google.cloud import bigquery
from google.cloud import storage
import logging
import uuid
import json
import urllib3
import socket
import requests
import os
import dataflow_pipeline.massive as pipeline
import cloud_storage_controller.cloud_storage_controller as gcscontroller
import datetime
import time

remover_api = Blueprint('remover_api', __name__)
########################### DEFINICION DE VARIABLES ###########################
fecha = time.strftime('%Y%m%d')

Ruta = ("/192.168.20.87", "media")[socket.gethostname()=="contentobi"]
KEY_REPORT = "remover"
fileserver_baseroute = ("//192.168.20.87", "/media")[socket.gethostname()=="contentobi"]

########################### CODIGO #####################################################################################

@remover_api.route("/" + KEY_REPORT)
def Ejecutar():
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('ct-telefonia')
    gcs_path = 'gs://ct-telefonia'
    ext = ".csv"

    blob1 = bucket.blob("agent_status/" + fecha + ext)
    blob2 = bucket.blob("cdr/" + fecha + ext)
    blob3 = bucket.blob("csat/" + fecha + ext)
    blob4 = bucket.blob("login_logout/" + fecha + ext)

    
    try:
        blob1.delete()
    except: 
        print("En la ruta: gs://ct-telefonia/agent_status/ No se encontraron archivos para borrar")
    
    try:
        blob2.delete()
    except: 
        print("En la ruta: gs://ct-telefonia/cdr/ No se encontraron archivos para borrar")
    
    try:
        blob3.delete()
    except: 
        print("En la ruta: gs://ct-telefonia/csat/ No se encontraron archivos para borrar")
    
    try:
        blob4.delete()
    except: 
        print("En la ruta: gs://ct-telefonia/login_logout/ No se encontraron archivos para borrar")
    
    return("Los archivos fueron eliminados con exito")
