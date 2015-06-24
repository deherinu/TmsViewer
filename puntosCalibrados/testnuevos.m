
%Graficar los puntos de referencia
center=[159.84620893  234.49256093  212.04649757]
mri_der=[281.23,  156.98,  121.07]
mri_izq=[39.165,  161.11 ,  116.81]
mri_nasion=[159.61 ,  195.91 ,   46.124]

figure(1);
title('Puntos MRI');
xlabel('Eje X')
ylabel('Eje Y')
zlabel('Eje Z')
hold on
%sien der
scatter3(mri_der(1),mri_der(2),mri_der(3),'+')
%sien izq
scatter3(mri_izq(1),mri_izq(2),mri_izq(3),'d')
%nasion
scatter3(mri_nasion(1),mri_nasion(2),mri_nasion(3),'*')
%sphere center
scatter3(center(1),center(2),center(3),'o')


[x,y,z] = sphere
r1=170
surf(r1*x+160,r1*y+234,r1*z+212)
colormap hsv
r2=20
r3=40
surf(r3*x+mri_der(1),r3*y+mri_der(2),r3*z+mri_der(3))
surf(r2*x+mri_izq(1),r2*y+mri_izq(2),r2*z+mri_izq(3))
surf(r2*x+mri_nasion(1),r2*y+mri_nasion(2),r2*z+mri_nasion(3))