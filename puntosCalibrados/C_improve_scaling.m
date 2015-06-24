function [ new_scaled_matrix ] = C_improve_scaling( data_1,data_2,rigid_Matrix, previous_scaled_matrix )
%C_IMPROVE_SCALING Summary of this function goes here
%   Detailed explanation goes here
    
    data_1=removerows(data_1,'ind',2)
    N = size(data_1,1);
    centroid_B = mean(data_2);
    eee=repmat(centroid_B, N, 1);
    data_2
    eee
    jojo=(data_2-eee);
    
    R=rigid_Matrix(1:3,1:3)
    
    centroid_Tms = mean(data_1);
    
    M = size(data_1,1);
        
    trans_tms_toCenter=data_1- repmat(centroid_Tms, M, 1);
    
    trans_tms_der_inCenter=[trans_tms_toCenter(1,:)'];
    trans_tms_izq_inCenter=[trans_tms_toCenter(2,:)'];
    trans_tms_nas_inCenter=[trans_tms_toCenter(3,:)'];
        
    rot_tms_der_inCenter=R*trans_tms_der_inCenter;
    rot_tms_izq_inCenter=R*trans_tms_izq_inCenter;
    rot_tms_nas_inCenter=R*trans_tms_nas_inCenter;
    
    match_der_inCenter=jojo(1,:);
    match_izq_inCenter=jojo(2,:);
    match_nas_inCenter=jojo(3,:);
   
    centerTms=[rot_tms_der_inCenter';rot_tms_izq_inCenter';rot_tms_nas_inCenter'];
    match_inCenter=[match_der_inCenter;match_izq_inCenter;match_nas_inCenter];
        
    scaleX1=1/(centerTms(1,1)/match_inCenter(1,1));
    scaleX2=1/(centerTms(2,1)/match_inCenter(2,1));
    scaleX3=1/(centerTms(3,1)/match_inCenter(3,1));
    
    scaleY1=1/(centerTms(1,2)/match_inCenter(1,2));
    scaleY2=1/(centerTms(2,2)/match_inCenter(2,2));
    scaleY3=1/(centerTms(3,2)/match_inCenter(3,2));
    
    scaleZ1=1/(centerTms(1,3)/match_inCenter(1,3));
    scaleZ2=1/(centerTms(2,3)/match_inCenter(2,3));
    scaleZ3=1/(centerTms(3,3)/match_inCenter(3,3));
    
    previous_scaled_matrix=previous_scaled_matrix(1:3,1:3)
    new_scaled_matrix=diag([mean([scaleX1,scaleX2]),mean([scaleY1,scaleY2,scaleY3]),mean([scaleZ1,scaleZ2,scaleZ3])])
    
    scaledDer=rot_tms_der_inCenter'*previous_scaled_matrix;
    scaledIzq=rot_tms_izq_inCenter'*previous_scaled_matrix;
    scaledNas=rot_tms_nas_inCenter'*previous_scaled_matrix;
    scaled_inCenter1=[scaledDer;scaledIzq;scaledNas];
    
    newscaledDer=rot_tms_der_inCenter'*new_scaled_matrix
    newscaledIzq=rot_tms_izq_inCenter'*new_scaled_matrix;
    newscaledNas=rot_tms_nas_inCenter'*new_scaled_matrix;
    scaled_inCenter2=[newscaledDer;newscaledIzq;newscaledNas];

    error1 = sum(sum(abs(match_inCenter-scaled_inCenter1)))
    error2= sum(sum(abs(match_inCenter-scaled_inCenter2)))
    
end

