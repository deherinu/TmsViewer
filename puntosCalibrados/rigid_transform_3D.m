%Referencias: 
%http://nghiaho.com/?page_id=671
%John_Vince_-_Mathematics_for_Computer_Graphics

%Funcion para hallar la rigidMatrix de transformacion (rotacion y translacion)
%dado un conjunto de puntos en 3 Dimensiones.
%Para esta funcion se deben ingresar al menos 3 puntos de camara y 3 puntos
%de mundo real



function [R,t] = rigid_transform_3D(A, B, C, D, E)

    path_trans='rigid_transforms/';
    
    
    %Verificar que la cantidad de parametros de entrada sean correctos (Dos matrices de entrada en este caso)
    if nargin ~= 5
	    error('Missing parameters');
    end
    
    %Verificar que los tamaños de las matrices sean iguales (La cantidad de puntos, Ej: dos matrices 3xN)
    %assert(size(A) == size(B))
    
    %Calcula la media de los puntos ingresados
    centroid_A = mean(A);
    centroid_B = mean(B);
    
    %Guarda la cantidad de puntos que tiene la rigidMatrix
    N = size(A,1);

    A
    
    %Repmat repite copias de la rigidMatrix
    uuu=repmat(centroid_A,N,1);
    sum(sum(A-uuu));
    jeje=(A-uuu)';
    eee=repmat(centroid_B, N, 1);
    jojo=(B-eee);
    H = (A - repmat(centroid_A, N, 1))' * (B - repmat(centroid_B, N, 1));
        
    [U,S,V] = svd(H);

    R = V*U';

    if det(R) < 0
        V(:,3)=V(:,3) * -1;
        R = V*U';
    end
    
    %Hallar vector de translacion
    t = -R*centroid_A' + centroid_B';
    %Matriz de translacion
    translationMatriz=[1 0 0 t(1);0 1 0 t(2);0 0 1 t(3);0 0 0 1];
    
    
    rigidMatrix=[R t];
    rigidMatrix=[rigidMatrix; 0 0 0 1]
    
    save(strcat(path_trans,'mTransRot','429','.mat'),'rigidMatrix')
    
    %Nuevos puntos
    punto1=[A(1,:)' ; 1]
    nuevopunto1=(rigidMatrix*punto1)'
    
    punto2=[A(2,:)' ; 1];
    nuevopunto2=(rigidMatrix*punto2)';
    
    punto3=[A(3,:)' ; 1];
    nuevopunto3=(rigidMatrix*punto3)';
    
    nuevopunto4=(rigidMatrix*C')';

    nuevos_puntos=[nuevopunto1(1:3);nuevopunto2(1:3);nuevopunto3(1:3);nuevopunto4(1:3)]
    error_nuevos = abs(B-nuevos_puntos(1:3,:))    
    
    %Iteraccion
    
    centroid_Tms = mean(E);
    
    M = size(E,1);
    
    trans_tms_toCenter=E - repmat(centroid_Tms, M, 1);
    
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
    
    previous_scaled_matrix=D(1:3,1:3);
    new_scaled_matrix=diag([mean([scaleX1,scaleX2]),mean([scaleY1,scaleY2,scaleY3]),mean([scaleZ1,scaleZ2,scaleZ3])])
    
    scaledDer=rot_tms_der_inCenter'*previous_scaled_matrix;
    scaledIzq=rot_tms_izq_inCenter'*previous_scaled_matrix;
    scaledNas=rot_tms_nas_inCenter'*previous_scaled_matrix;
    scaled_inCenter1=[scaledDer;scaledIzq;scaledNas];
    
    newscaledDer=rot_tms_der_inCenter'*new_scaled_matrix
    newscaledIzq=rot_tms_izq_inCenter'*new_scaled_matrix;
    newscaledNas=rot_tms_nas_inCenter'*new_scaled_matrix;
    scaled_inCenter2=[newscaledDer;newscaledIzq;newscaledNas];

    error1 = sum(sum(abs(match_inCenter-scaled_inCenter1)));
    error2= sum(sum(abs(match_inCenter-scaled_inCenter2)));
    
    [scaled_inCenter2(1,:)';1]
    new_points1=translationMatriz*[scaled_inCenter2(1,:)';1];
    new_points2=translationMatriz*[scaled_inCenter2(2,:)';1];
    new_points3=translationMatriz*[scaled_inCenter2(3,:)';1];
    new_points=[new_points1';new_points2';new_points3']
        
%     figure(1)
%     scatter3(jeje(1,1),jeje(1,2),jeje(1,3),'filled','MarkerFaceColor',[0 .75 .75],'MarkerEdgeColor',[1 0 0])
%     hold on
%     scatter3(jeje(2,1),jeje(2,2),jeje(2,3),'filled','MarkerFaceColor',[.5 .2 .2],'MarkerEdgeColor',[1 0 0])
%     scatter3(jeje(3,1),jeje(3,2),jeje(3,3),'filled','MarkerFaceColor',[0 .9 .9],'MarkerEdgeColor',[1 0 0])
%     
%     scatter3(jojo(1,1),jojo(1,2),jojo(1,3),'filled','MarkerFaceColor',[0 .75 .75])
%     hold on
%     scatter3(jojo(2,1),jojo(2,2),jojo(2,3),'filled','MarkerFaceColor',[.5 .2 .2])
%     scatter3(jojo(3,1),jojo(3,2),jojo(3,3),'filled','MarkerFaceColor',[0 .9 .9])
       
%     figure(3)
%     title('Puntos nuevos');
%     xlabel('Eje X')
%     ylabel('Eje Y')
%     zlabel('Eje Z')
%     hold on
%     %Sien Derecha
%     scatter3(nuevos_puntos(1,1),nuevos_puntos(1,2),nuevos_puntos(1,3),'+')
%     hold on
%     %Sien Izquierda
%     scatter3(nuevos_puntos(2,1),nuevos_puntos(2,2),nuevos_puntos(2,3),'d')
%     hold on
%     %Nasion
%     scatter3(nuevos_puntos(3,1),nuevos_puntos(3,2),nuevos_puntos(3,3),'*')
%     %Vertex
%     scatter3(nuevos_puntos(4,1),nuevos_puntos(4,2),nuevos_puntos(4,3),'o')
    
end