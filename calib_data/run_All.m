clear all
clc

%Read data
c_points='calib_points/TMS-429.csv';
calib_points=csvread(c_points);
%Read calibration points TMS
filename='calib_pills/tms/TMS-429.csv';
calib_tms_pills=csvread(filename)
%Load pills positions MRI
load('calib_pills/mri/429.mat');
pos_pills_mri
%load as pos_pills_mri

%Auxiliar variable
scaling_Matrix=zeros(4);

if ~any(scaling_Matrix(:))

    [scaled_Points,data_2, scaling_Matrix]=A_scaled_Points(calib_tms_pills,pos_pills_mri,scaling_Matrix);
    
    copy_scaled_Points=scaled_Points
    scaled_Points=removerows(scaled_Points,'ind',2);
    
    [rigid_Matrix]=B_rigid_transformation_3D(scaled_Points,data_2);

    %[new_scaling_Matrix]=C_improve_scaling(tms_points,posiciones,rigid_Matrix,scaling_Matrix)

    punto1=[copy_scaled_Points(1,:)' ; 1];
    punto2=[copy_scaled_Points(2,:)' ; 1];
    punto3=[copy_scaled_Points(3,:)' ; 1];
    punto4=[copy_scaled_Points(4,:)' ; 1];

    new_point1=(rigid_Matrix*punto1)';
    new_point2=(rigid_Matrix*punto2)';
    new_point3=(rigid_Matrix*punto3)';
    new_point4=(rigid_Matrix*punto4)';

    new_calib_data=[new_point1(1:3);new_point2(1:3);new_point3(1:3);new_point4(1:3)]
    
    csvwrite('calib_pills/tms/new_pos/TMS-429.csv', new_calib_data);
    
    %error2= sum(sum(abs(pos_pills_mri-new_calib_data)))
    
else
    disp('...')
end

%Calculate new data
new_data_matrix=[];

for i=1:size(calib_points,1)
    
    %Calculate new obj positions
    obj_point=[calib_points(i,9),calib_points(i,10),calib_points(i,11),1]';
    obj_point_scaled=scaling_Matrix*obj_point;
    new_obj_point=rigid_Matrix*obj_point_scaled;
    new_obj_point=new_obj_point(1:3)';
    
    %Calculate new refer positions    
    refer_pos=[calib_points(i,2),calib_points(i,3),calib_points(i,4),1]';
    refer_pos_scaled=scaling_Matrix*refer_pos;
    new_refer_pos=rigid_Matrix*refer_pos_scaled;
    new_refer_pos=new_refer_pos(1:3)';
        
    %Create new data matrix
    new_data_matrix=[new_data_matrix;new_obj_point(1),new_obj_point(2),new_obj_point(3),new_refer_pos(1),new_refer_pos(2),new_refer_pos(3)];
    
    %Save csv
    csvwrite('calib_points/new_pos/TMS-429.csv', new_data_matrix);
    
end
