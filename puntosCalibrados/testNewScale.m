clear all
clc
tms=[0.7265    1.2057   -0.9838;0.7150    1.2059   -0.8492;0.6801    1.2221   -0.9188];
mri=[281   156   123;39   160   119;160   198    42];

%new_scale=[1.792485938109180 0 0 0;0 2.081558026169658 0 0;0 0 2.008237461415154 0;0 0 0 0.001]*1000;
new_scale=[ 1.792388501314397 0 0 0;0 1.864581489353677 0 0;0 0 1.860391800458227 0;0 0 0 0.001]*1000;


scaled_der=[tms(1,:)';1]'*new_scale;
scaled_izq=[tms(2,:)';1]'*new_scale;
scaled_nasion=[tms(3,:)';1]'*new_scale;
scaled=[scaled_der(1:3);scaled_izq(1:3);scaled_nasion(1:3)]

[R,t]=original(scaled,mri);

rigid_matrix=[R t;0 0 0 1];

new_point1=(rigid_matrix*scaled_der')';
new_point2=(rigid_matrix*scaled_izq')';
new_point3=(rigid_matrix*scaled_nasion')';

mri
new_points=[new_point1;new_point2;new_point3]

error2= sum(sum(abs(mri-new_points(1:3,1:3))))