function [scaled_Points,data_2, scaling_Matrix] = A_scaled_Points(data_1,data_2,scaling_Matrix)
%FIRSTSCALING Calculate scaling matrix to convert dataset Data1 points to
%dataset Data2 points scale
%   Usage: 

    if ~any(scaling_Matrix(:))

        %Load Data1
        %Our case p1 -> Right temple, p2 -> Nasion, p3 -> Left temple
        p1_data1=data_1(1,:);
        p2_data1=data_1(3,:);
        p3_data1=data_1(4,:);
        %Vertex
        p4_data1=data_1(2,:);

        %Load Data2
        %Our case p1 -> Right temple, p2 -> Nasion, p3 -> Left temple
        p1_data2=data_2(1,:);
        p2_data2=data_2(2,:);
        p3_data2=data_2(3,:);

        %Calculate distance between Data1 points
        dist_p1_p2_data1=norm(p1_data1-p2_data1);
        dist_p2_p3_data1=norm(p2_data1-p3_data1);
        dist_p3_p1_data1=norm(p3_data1-p1_data1);

        %Calculate distance between Data2 points
        dist_p1_p2_data2=norm(p1_data2-p2_data2);
        dist_p2_p3_data2=norm(p2_data2-p3_data2);
        dist_p3_p1_data2=norm(p3_data2-p1_data2);

        %Scale factor
        scale_factor_1=(1/(dist_p1_p2_data1/dist_p1_p2_data2));
        scale_factor_2=(1/(dist_p2_p3_data1/dist_p2_p3_data2));
        scale_factor_3=(1/(dist_p3_p1_data1/dist_p3_p1_data2));
        %scale_factor=(scale_factor_1+scale_factor_2+scale_factor_3)/3;

        %Create Scaling Matrix
        diagonal=[scale_factor_1 scale_factor_2 scale_factor_3 1];
        scaling_Matrix=diag(diagonal);

        %Calculate scaled points and return
        scaled_point1=scaling_Matrix*[p1_data1';1];
        scaled_point2=scaling_Matrix*[p4_data1';1];
        scaled_point3=scaling_Matrix*[p2_data1';1];
        scaled_point4=scaling_Matrix*[p3_data1';1];
        scaled_Points=[scaled_point1(1:3)';scaled_point2(1:3)';scaled_point3(1:3)';scaled_point4(1:3)'];
    else
        disp('uuuuu');
    end     
end

