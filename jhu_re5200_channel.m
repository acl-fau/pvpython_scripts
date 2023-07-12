%******************Channel Flow Re = 1000*************************
clear all;
close all;

authkey = 'edu.jhu.pha.turbulence.testing-201406';
dataset = 'channel5200'; %channel5200

% ---- Temporal Interpolation Options ----
NoTInt   = 'None' ; % No temporal interpolation
PCHIPInt = 'PCHIP'; % Piecewise cubic Hermit interpolation in time

% ---- Spatial Interpolation Flags for getVelocity & getVelocityAndPressure ----
NoSInt = 'None'; % No spatial interpolation
Lag4   = 'Lag4'; % 4th order Lagrangian interpolation in space
Lag6   = 'Lag6'; % 6th order Lagrangian interpolation in space
Lag8   = 'Lag8'; % 8th order Lagrangian interpolation in space

% ---- Spatial Differentiation & Interpolation Flags for getVelocityGradient & getPressureGradient ----
FD4NoInt = 'None_Fd4' ; % 4th order finite differential scheme for grid values, no spatial interpolation
FD6NoInt = 'None_Fd6' ; % 6th order finite differential scheme for grid values, no spatial interpolation
FD8NoInt = 'None_Fd8' ; % 8th order finite differential scheme for grid values, no spatial interpolation
FD4Lag4  = 'Fd4Lag4'  ; % 4th order finite differential scheme for grid values, 4th order Lagrangian interpolation in space

% ---- Spline interpolation and differentiation Flags for getVelocity,
% getPressure, getVelocityGradient, getPressureGradient,
% getVelocityHessian, getPressureHessian
M1Q4   = 'M1Q4'; % Splines with smoothness 1 (3rd order) over 4 data points. Not applicable for Hessian.
M2Q8   = 'M2Q8'; % Splines with smoothness 2 (5th order) over 8 data points.
M2Q14   = 'M2Q14'; % Splines with smoothness 2 (5th order) over 14 data points.

%x_spacing = 8*pi/2048*10;
%z_spacing = 3*pi/1536;

nx = 10240;
nz = 7680;

npoints = nx*nz;

time = 0.364; %time-step to sample

yoff = 1 - 0.058149; %y+ = 300, u_tau = 0.04148722, nu = 8e-6 

x = linspace(0, 8*pi, nx);
z = linspace(0, 3*pi, nz);

[X Z] = meshgrid(x, z);
points = zeros(3,npoints);
points(1,:) = X(:)';
points(3,:) = Z(:)';
points(2,:) = yoff;

%velocity  = zeros(3,npoints);

query_no = 4000;

fprintf('\nRequesting velocity gradients at %i points %i at a time\n',npoints, query_no);

nblocks = floor(npoints/query_no);
grad_vel = zeros(9,query_no,nblocks);
%grad_vel = zeros(9,npoints);


tic
parfor ind = 1:nblocks
    i = (ind-1)*query_no+1;
    count=1;
    while count<100
        try
            temp = getVelocityGradient(authkey, dataset, time,  FD4Lag4, NoTInt, query_no, points(:,i:i+query_no-1));
            grad_vel(:,:,ind) = temp;
            fprintf('\n %i out of %i done\n',ind,nblocks);
            count=100;
        catch
            fprintf('\nGonna pause for 10 min for the %i time',count);
            pause(600);
            count = count+1;
        end
    end
end
toc
% for ind = 1:nblocks
%     i = (ind-1)*query_no+1;
%     temp = getVelocityGradient(authkey, dataset, time,  FD4Lag4, NoTInt, query_no, points(:,i:i+query_no-1));
%     grad_vel(:,:,ind) = temp;
%    
%     fprintf('\n %i out of %i done\n',ind,nblocks);
% end
% 
grad_vel = reshape(grad_vel,[9,query_no*nblocks]);

i = nblocks*query_no+1;
temp = getVelocityGradient (authkey, dataset, time,  FD4Lag4, NoTInt, npoints-i+1, points(:,i:end));
grad_vel = [grad_vel temp];
% toc

fprintf('\nSaving..\n');
save("Re5200_channel_yplus300.mat","grad_vel")
fprintf('\nSaved\n');