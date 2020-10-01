#coding: utf-8 
from __future__ import print_function, absolute_import

import logging
import re
import json
import requests
import uuid
import time
import os
import argparse
import uuid
import datetime
import socket

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.io.filesystems import FileSystems
from apache_beam.metrics import Metrics
from apache_beam.metrics.metric import MetricsFilter
from apache_beam import pvalue
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

TABLE_SCHEMA = (
		
		'idkey:STRING, '
		'fecha:STRING, '
		'NUMERO_DEL_CASO_CLIENTE:STRING, '
		'TIPO_ID_CLIENTE:STRING, '
		'NUMERO_DE_IDENTIFICACION:STRING, '
		'NOMBRE_DE_LA_CUENTA:STRING, '
		'SEGMENTO_COMERCIAL:STRING, '
		'FECHA_DE_APERTURA:STRING, '
		'FECHA_ESPERADA_SOLUCION:STRING, '
		'FECHA_DE_CIERRE:STRING, '
		'ORIGEN_DEL_CASO:STRING, '
		'CREADO_POR:STRING, '
		'CLIENTE_CSC:STRING, '
		'TIPO_DE_SOLICITUD:STRING, '
		'TIPO_DE_REGISTRO_DEL_CASO:STRING, '
		'ESTADO:STRING, '
		'VENCIMIENTO_OFERTA:STRING, '
		'DERECHO_DE_PETICION:STRING, '
		'REMITENTE:STRING, '
		'TEMA_SIN_APELLIDO:STRING, '
		'DETALLE_SIN_APELLIDO:STRING, '
		'DESCRIPCION:STRING, '
		'LINEA_DE_NEGOCIO:STRING, '
		'AMPLIACION_TERMINOS:STRING, '
		'PROPIETARIO_DEL_CASO:STRING, '
		'MOTIVO_AMPLIACION_TERMINOS:STRING, '
		'CASO_PRIORIZADO:STRING, '
		'ATRIBUTO_ESCALAMIENTO:STRING, '
		'CONTACTO_CORREO_ELECTRONICO:STRING, '
		'NOMBRE_DEL_CONTACTO:STRING '




)
# ?
class formatearData(beam.DoFn):

	def __init__(self, mifecha):
		super(formatearData, self).__init__()
		self.mifecha = mifecha
	
	def process(self, element):
		# print(element)
		arrayCSV = element.split(';')

		tupla= {'idkey' : str(uuid.uuid4()),
				# 'fecha' : datetime.datetime.today().strftime('%Y-%m-%d'),
				'fecha': self.mifecha,
				'NUMERO_DEL_CASO_CLIENTE' : arrayCSV[0],
				'TIPO_ID_CLIENTE' : arrayCSV[1],
				'NUMERO_DE_IDENTIFICACION' : arrayCSV[2],
				'NOMBRE_DE_LA_CUENTA' : arrayCSV[3],
				'SEGMENTO_COMERCIAL' : arrayCSV[4],
				'FECHA_DE_APERTURA' : arrayCSV[5],
				'FECHA_ESPERADA_SOLUCION' : arrayCSV[6],
				'FECHA_DE_CIERRE' : arrayCSV[7],
				'ORIGEN_DEL_CASO' : arrayCSV[8],
				'CREADO_POR' : arrayCSV[9],
				'CLIENTE_CSC' : arrayCSV[10],
				'TIPO_DE_SOLICITUD' : arrayCSV[11],
				'TIPO_DE_REGISTRO_DEL_CASO' : arrayCSV[12],
				'ESTADO' : arrayCSV[13],
				'VENCIMIENTO_OFERTA' : arrayCSV[14],
				'DERECHO_DE_PETICION' : arrayCSV[15],
				'REMITENTE' : arrayCSV[16],
				'TEMA_SIN_APELLIDO' : arrayCSV[17],
				'DETALLE_SIN_APELLIDO' : arrayCSV[18],
				'DESCRIPCION' : arrayCSV[19],
				'LINEA_DE_NEGOCIO' : arrayCSV[20],
				'AMPLIACION_TERMINOS' : arrayCSV[21],
				'PROPIETARIO_DEL_CASO' : arrayCSV[22],
				'MOTIVO_AMPLIACION_TERMINOS' : arrayCSV[23],
				'CASO_PRIORIZADO' : arrayCSV[24],
				'ATRIBUTO_ESCALAMIENTO' : arrayCSV[25],
				'CONTACTO_CORREO_ELECTRONICO' : arrayCSV[26],
				'NOMBRE_DEL_CONTACTO' : arrayCSV[27]

				}
		
		return [tupla]



def run(archivo, mifecha):

	gcs_path = "gs://ct-dispersion" #Definicion de la raiz del bucket
	gcs_project = "contento-bi"

	mi_runer = ("DirectRunner", "DataflowRunner")[socket.gethostname()=="contentobi"]
	pipeline =  beam.Pipeline(runner=mi_runer, argv=[
        "--project", gcs_project,
        "--staging_location", ("%s/dataflow_files/staging_location" % gcs_path),
        "--temp_location", ("%s/dataflow_files/temp" % gcs_path),
        "--output", ("%s/dataflow_files/output" % gcs_path),
        "--setup_file", "./setup.py",
        "--max_num_workers", "10",
		"--subnetwork", "https://www.googleapis.com/compute/v1/projects/contento-bi/regions/us-central1/subnetworks/contento-subnet1"
        # "--num_workers", "30",
        # "--autoscaling_algorithm", "NONE"		
	])
	
	# lines = pipeline | 'Lectura de Archivo' >> ReadFromText("gs://ct-bancolombia/info-segumiento/BANCOLOMBIA_INF_SEG_20181206 1100.csv", skip_header_lines=1)
	#lines = pipeline | 'Lectura de Archivo' >> ReadFromText("gs://ct-bancolombia/info-segumiento/BANCOLOMBIA_INF_SEG_20181129 0800.csv", skip_header_lines=1)
	lines = pipeline | 'Lectura de Archivo' >> ReadFromText(archivo, skip_header_lines=1)

	transformed = (lines | 'Formatear Data' >> beam.ParDo(formatearData(mifecha)))

	# lines | 'Escribir en Archivo' >> WriteToText("archivos/Info_carga_banco_prej_small", file_name_suffix='.csv',shard_name_template='')

	# transformed | 'Escribir en Archivo' >> WriteToText("archivos/Info_carga_banco_seg", file_name_suffix='.csv',shard_name_template='')
	#transformed | 'Escribir en Archivo' >> WriteToText("gs://ct-bancolombia/info-segumiento/info_carga_banco_seg",file_name_suffix='.csv',shard_name_template='')

	transformed | 'Escritura a BigQuery base' >> beam.io.WriteToBigQuery(
		gcs_project + ":proteccion.sales", 
		schema=TABLE_SCHEMA, 
		create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED, 
		write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
		)

	# transformed | 'Borrar Archivo' >> FileSystems.delete('gs://ct-avon/prejuridico/AVON_INF_PREJ_20181111.TXT')
	# 'Eliminar' >> FileSystems.delete (["archivos/Info_carga_avon.1.txt"])

	jobObject = pipeline.run()
	# jobID = jobObject.job_id()

	return ("Corrio Full HD")



