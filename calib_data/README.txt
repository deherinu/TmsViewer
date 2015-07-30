Instrucciones para crear una única rutina

1. Se debe tener un archivo csv con las posiciones de las píldoras de todos los sujetos, el formato es el siguiente:

sujeto,izqX,izqY,izqZ,nasX,nasY,nasZ,derX,derY,derZ
429,-0.3,58.9,56.6,18.7,95.4,-0.6,-0.8,54.8,-63.8

2. Ejecutar el script gen_posc_pills, lo cual genera archivos.mat con las posiciones de las pildoras por cada sujeto

calib_pills/mri/429.mat

Esta matriz se puede cargar mediante el comando load('calib_pills/mri/429.mat'). Nombre de la variable que contiene la matriz en el archivo .mat

Los archivos contienen una variable "pos_pills_mri" la cual puede ser llamada desde la ventana de comandos

3. El visualizador genera un archivo csv con las posiciones de las pildoras en el examen TMS.

calib_pills/tms/TMS-429.csv

Este archivo se puede cargar en MATLAB

filename='../new_data/calib_pills/tms/TMS-429.csv';
tms_points=csvread(filename);

4. Lo primero que se debe calcular es la matriz de escalamiento y los puntos nuevos escalados. Se calcula en el script A_scaled_Points.m

Esta funcion recibe como parametros los puntos del examen TMS, y los de MRI de las pildoras en coordenadas de mundo

A_scaled_Points(TMS,MRI)

5.  