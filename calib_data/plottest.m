%plot test

filename='plottest.csv';
points=csvread(filename)

%right
scatter3(-64.583,55.397,-0.49232,'filled')
hold on
%vertex
scatter3(0.81314,87.617,-140.4,'*')
%nasion
scatter3(-4.9985,93.286,17.626,'filled')
%left
scatter3(55.781,60.416,0.46614,'filled')
%other
scatter3(-4.2,74.3,69.7,'o')
%corners
scatter3(236,159,160,'s')
scatter3(237,1069,175,'s')
scatter3(-671,159,213,'s')
scatter3(-671,1069,227,'s')
scatter3(273,149,777,'s')
scatter3(274,1059,792,'s')
scatter3(-635,149,829,'s')
scatter3(-634,1059,844,'s')


for i=1:size(points,1)
    scatter3(points(i,1),points(i,2),points(i,3))
    hold on
    points(i,:)
end