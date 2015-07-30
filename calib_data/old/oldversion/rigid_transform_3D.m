%Referencias: 
%http://nghiaho.com/?page_id=671
%John_Vince_-_Mathematics_for_Computer_Graphics

%Funcion para hallar la matriz de transformacion (rotacion y translacion)
%dado un conjunto de puntos en 3 Dimensiones.
%Para esta funcion se deben ingresar al menos 3 puntos de camara y 3 puntos
%de mundo real

function [R,t] = rigid_transform_3D(A, B, C)
    
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
    t = -R*centroid_A' + centroid_B';
    
    A
    B
    
    matriz=[R t];
    matriz=[matriz; 0 0 0 1]
        
    punto1=[A(1,:)' ; 1]
    nuevopunto1=(matriz*punto1)
    
    punto2=[A(2,:)' ; 1]
    nuevopunto2=(matriz*punto2)';
    
    punto3=[A(3,:)' ; 1]
    nuevopunto3=(matriz*punto3)';
    
    %nuevopunto4=(matriz*C)';

    nuevos_puntos=[nuevopunto1(1:3);nuevopunto2(1:3);nuevopunto3(1:3)]
    
    error_nuevos = [ abs(B(1,1)-nuevos_puntos(1,1)) abs(B(1,2)-nuevos_puntos(1,2)) abs(B(1,3)-nuevos_puntos(1,3)) ; abs(B(2,1)-nuevos_puntos(2,1)) abs(B(2,2)-nuevos_puntos(2,2)) abs(B(2,3)-nuevos_puntos(2,3)) ;abs(B(3,1)-nuevos_puntos(3,1)) abs(B(3,2)-nuevos_puntos(3,2)) abs(B(3,3)-nuevos_puntos(3,3)) ];
    
    figure(3)
    title('Puntos nuevos');
    xlabel('Eje X')
    ylabel('Eje Y')
    zlabel('Eje Z')
    hold on
    %Sien Derecha
    scatter3(nuevos_puntos(1,1),nuevos_puntos(1,2),nuevos_puntos(1,3),'+')
    hold on
    %Sien Izquierda
    scatter3(nuevos_puntos(2,1),nuevos_puntos(2,2),nuevos_puntos(2,3),'d')
    hold on
    %Nasion
    scatter3(nuevos_puntos(3,1),nuevos_puntos(3,2),nuevos_puntos(3,3),'*')
    %Vertex
    %scatter3(nuevos_puntos(4,1),nuevos_puntos(4,2),nuevos_puntos(4,3),'o')
    
end