function [rigid_Matrix] = B_rigid_transformation_3D(data_1,data_2)
%RIGID_TRANSFORMATION_3D Summary of this function goes here
%   Detailed explanation goes here

    path_trans='rigid_transforms/';

    %Verificar que la cantidad de parametros de entrada sean correctos (Dos matrices de entrada en este caso)
    if nargin ~= 2
	    error('Missing parameters');
    end
    
    %Verificar que los tamaños de las matrices sean iguales (La cantidad de puntos, Ej: dos matrices 3xN)
    %assert(size(data_1) == size(data_2))
    
    %Calcula la media de los puntos ingresados
    centroid_data_1 = mean(data_1);
    centroid_data_2 = mean(data_2);
    
    %Guarda la cantidad de puntos que tiene la rigidMatrix
    N = size(data_1,1);
    
    %Repmat repite copias de la rigidMatrix
    H = (data_1 - repmat(centroid_data_1, N, 1))' * (data_2 - repmat(centroid_data_2, N, 1));
        
    [U,S,V] = svd(H);

    R = V*U';

    if det(R) < 0
        V(:,3)=V(:,3) * -1;
        R = V*U';
    end
    
    %Translation vector
    t = -R*centroid_data_1' + centroid_data_2';
    
    %Translation matrix
    %translation_Matrix=[1 0 0 t(1);0 1 0 t(2);0 0 1 t(3);0 0 0 1];
    
    %Rigid transformation
    rigid_Matrix=[R t];
    rigid_Matrix=[rigid_Matrix; 0 0 0 1];
    
    %Save rigid matrix
    save(strcat(path_trans,'mTransRot','429','.mat'),'rigid_Matrix')    
    
end

