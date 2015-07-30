%Graficar los puntos de referencia
tms_der=[0.72653299239763558,1.2057049084853007,-0.9837620190934584];
tms_ver=[0.8179758081439471,1.3257029897975521,-0.90233975047597215];
tms_nas=[0.68013381852991117,1.2220864913239109,-0.91884434574933682];
tms_izq=[0.71504846989072801,1.2058866102228925,-0.84919908227022156];

tms = [tms_der; tms_ver; tms_nas; tms_izq];

mri_der=[-0.8,54.8,-63.8];
mri_nas=[18.7,95.4,-6.1];
mri_izq=[-0.3,58.9,56.6];

mri_other=[-4.2,74.3,69.7];

mri = [mri_der; mri_nas; mri_izq];

%Auxiliar variable
scaling_Matrix=zeros(4);

if ~any(scaling_Matrix(:))

    [scaled_Points,data_2, scaling_Matrix]=A_scaled_Points(tms,mri,scaling_Matrix);
    
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
    
    %csvwrite('calib_pills/tms/new_pos/TMS-429.csv', new_calib_data);
    
    %error2= sum(sum(abs(pos_pills_mri-new_calib_data)))
    
else
    disp('...')
end