%Referencias: 
%http://nghiaho.com/?page_id=671
%John_Vince_-_Mathematics_for_Computer_Graphics

%Funcion para hallar la matriz de transformacion (rotacion y translacion)
%dado un conjunto de puntos en 3 Dimensiones.
%Para esta funcion se deben ingresar al menos 3 puntos de camara y 3 puntos
%de mundo real



function [R,t] = rigid_transform_3D(A, B)
    
    %Verificar que la cantidad de parametros de entrada sean correctos (Dos matrices de entrada en este caso)
    if nargin ~= 2
	    error('Missing parameters');
    end
    
    %Verificar que los tamaños de las matrices sean iguales (La cantidad de puntos, Ej: dos matrices 3xN)
    %assert(size(A) == size(B))

    %Calcula la media de los puntos ingresados
    centroid_A = mean(A);
    centroid_B = mean(B);
    
    %Guarda la cantidad de puntos que tiene la matriz
    N = size(A,1);
    
    %repmat repite copias de la matriz
    H = (A - repmat(centroid_A, N, 1))' * (B - repmat(centroid_B, N, 1));
        
    [U,S,V] = svd(H);

    R = V*U';

    if det(R) < 0
        V(:,3)=V(:,3) * -1;
        R = V*U';
    end
    
    %Hallar vector de translacion
    t = -R*centroid_A' + centroid_B'
end