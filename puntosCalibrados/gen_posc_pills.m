clear all
clc
file='pills.csv'
mat_file=csvread(file)

for i=1:size(mat_file)
    name=mat_file(i,1)
    der=mat_file(i,2:4)
    nas=mat_file(i,5:7)
    izq=mat_file(i,8:10)
    pos_pills_mri=[der;nas;izq]
    nombre=strcat(num2str(name),'.mat')
    save(nombre,'pos_pills_mri')
end