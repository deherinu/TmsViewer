%Cargar las matrices
load('calib_pills/mri/429.mat');
filename='calib_pills/tms/TMS-429.csv';
tms_points=csvread(filename);
scaling_matrix=[];

%Primer script, buscar escalamiento
[scaled_points, mri, scaling_matrix] = A_scaled_Points(tms_points, pos_pills_mri, scaling_matrix);

%Quitar vertex para hallar la matriz
scaled_points_temp = removerows(scaled_points,'ind',2);

%Segundo script, hallar transformacion rigida
[rigid_matrix] = B_rigid_transformation_3D(scaled_points_temp, mri);

%Apply rigid matrix to scaled points
new_point1=rigid_matrix*[scaled_points(1,:)';1]
new_point2=rigid_matrix*[scaled_points(2,:)';1]
new_point3=rigid_matrix*[scaled_points(3,:)';1]
new_point4=rigid_matrix*[scaled_points(4,:)';1]

new_points = [new_point1';new_point2';new_point3';new_point4']
new_points = new_points(:,1:3)

%Create csv with new points
csvwrite('calib_pills/tms/new_pos/TMS-429.csv',new_points)