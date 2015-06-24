clear all
clc

%Lectura archivos posc pildoras en tms y mri

filename='calib_pills/calib_pills_429.csv';
M=csvread(filename);

load('calib_pills/429.mat');
path_trans='rigid_transforms/';

%Guardar variables con las posiciones 

tms_der=M(1,:)
tms_vertex=M(2,:);
tms_nasion=M(3,:);
tms_izq=M(4,:);
tms=[tms_der;tms_izq;tms_nasion]

mri_der=posiciones(1,:);
mri_nasion=posiciones(2,:);
mri_izq=posiciones(3,:);
mri=[mri_der;mri_izq;mri_nasion]


%Ejemplo Unity
% mri_der=[2.48 0.77 1.14];
% mri_izq=[2.48 0.77 4.14];
% mri_nasion=[2.48 3.77 1.14];
% 
% tms_der=[-3.4862 -0.61529 1.3849];
% tms_izq=[3.6062 0.49695 -1.1554];
% tms_nasion=[-3.6062 6.4771 4.1554];


%Funcion de escalamiento 

%Hallar distancias

%Entre tms sienes
dist_tms_sienes=norm(tms_der-tms_izq);
%Entre tms sienizq nasion
dist_tms_izq_nasion=norm(tms_izq-tms_nasion);
%Entre tms siender nasion
dist_tms_der_nasion=norm(tms_der-tms_nasion);

%mri sienes
dist_mri_sienes=norm(mri_der-mri_izq);
%tms sienizq nasion
dist_mri_izq_nasion=norm(mri_izq-mri_nasion);
%tms siender nasion
dist_mri_der_nasion=norm(mri_der-mri_nasion);

% Razon entre los dos sistemas de puntos
escala_sienes=(1/(dist_tms_sienes/dist_mri_sienes));
escala_izq_nasion=(1/(dist_tms_izq_nasion/dist_mri_izq_nasion));
escala_der_nasion=(1/(dist_tms_der_nasion/dist_mri_der_nasion));

escala=(escala_sienes+escala_izq_nasion+escala_der_nasion)/3;

%Generar matriz de escalamiento
%diagonal=[escala escala escala 1];
diagonal=[escala_sienes escala_izq_nasion escala_der_nasion 1];
matriz_escalamiento=diag(diagonal)
save(strcat(path_trans,'mScale','429','.mat'),'matriz_escalamiento')

%Generacion puntos escalados
temp_der=[tms_der' ; 1];
temp_izq=[tms_izq' ; 1];
temp_nasion=[tms_nasion' ; 1];
temp_vertex=[tms_vertex' ; 1];

%multiplicar nuevos puntos por la matriz de escalamiento
escalada_der=(matriz_escalamiento*temp_der)';
escalada_izq=(matriz_escalamiento*temp_izq)';
escalada_nasion=(matriz_escalamiento*temp_nasion)';
escalada_vertex=(matriz_escalamiento*temp_vertex)';

%Distancias
%Entre tms sienes
dist_esca1=norm(escalada_der(1:3)-escalada_izq(1:3));
%Entre tms sienizq nasion
dist_esca2=norm(escalada_izq(1:3)-escalada_nasion(1:3));
%Entre tms siender nasion
dist_esca3=norm(escalada_der(1:3)-escalada_nasion(1:3));

distancias=[dist_mri_sienes dist_mri_izq_nasion dist_mri_der_nasion;dist_esca1 dist_esca2 dist_esca3];

%parametros para funcion de rotacion translacion

A=[escalada_der(1:3);escalada_izq(1:3);escalada_nasion(1:3)];
B=[mri_der;mri_izq;mri_nasion];

rigid_transform_3D(A,B,escalada_vertex,matriz_escalamiento,tms);

% %Graficar los puntos de referencia
% figure(1);
% title('Puntos MRI');
% xlabel('Eje X')
% ylabel('Eje Y')
% zlabel('Eje Z')
% hold on
% %sien der
% scatter3(mri_der(1),mri_der(2),mri_der(3),'+')
% %sien izq
% scatter3(mri_izq(1),mri_izq(2),mri_izq(3),'d')
% %nasion
% scatter3(mri_nasion(1),mri_nasion(2),mri_nasion(3),'*')
% 
% figure(2);
% title('Puntos tms');
% xlabel('Eje X')
% ylabel('Eje Y')
% zlabel('Eje Z')
% hold on
% %Sien Derecha
% scatter3(tms_der(1),tms_der(2),tms_der(3),'+')
% hold on
% %Sien Izquierda
% scatter3(tms_izq(1),tms_izq(2),tms_izq(3),'d')
% hold on
% %Nasion
% scatter3(tms_nasion(1),tms_nasion(2),tms_nasion(3),'*')



