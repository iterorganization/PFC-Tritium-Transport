R_Top = 3.969425;
R_Bottom = 4.163925;
Z_Top = -2.544000;
Z_Bottom = -3.911604;

R_EOR = [
4.1607
4.285489
4.361321
4.415685
4.472034
4.505336
4.521451
4.508417
4.450079
4.356188
4.25381
4.177015
];

Z_EOR = [
-2.567545
-2.625938
-2.685485
-2.745929
-2.838186
-2.92992
-3.040377
-3.17555
-3.32492
-3.517411
-3.727313
-3.884761
];

Angle_EOR = [
1.898508
2.128549
2.134799
2.086304
2.133364
2.134478
2.441925
2.556727
2.910893
3.337397
3.737257
3.97227
];

R_interm = [
4.123131
4.235462
4.299562
4.352196
4.408393
4.444229
4.480723
4.504114
4.520161
4.521736
4.512184
4.488882
4.422292
4.341949
4.236276
4.177015
];

Z_interm = [
-2.557323
-2.597565
-2.63533
-2.677026
-2.736613
-2.787223
-2.857491
-2.925242
-3.018407
-3.065482
-3.157866
-3.240061
-3.381861
-3.546615
-3.76327
-3.884761
];

Angle_interm = [
2.548838
2.438305
2.454424
2.333024
2.029306
1.945001
1.786097
1.703766
1.660162
1.583425
1.596409
1.6002
1.914067
2.263117
2.68469
2.887772
];

R_EOD = [
4.1607
4.261283
4.335282
4.407244
4.449832
4.490321
4.514771
4.521651
4.518807
4.499374
4.443497
4.377838
4.29577
4.236276
4.188226
];

Z_EOD = [
-2.567545
-2.611289
-2.662387
-2.735193
-2.796445
-2.881767
-2.974309
-3.048182
-3.114315
-3.209259
-3.338408
-3.473023
-3.641281
-3.76327
-3.861777
];

Angle_EOD = [
2.815796
2.74636
2.34536
1.92044
1.5821
1.288477
1.0082
0.901512
0.724228
0.546261
0.716161
1.004798
1.29433
1.49621
1.636625
];

% polygonal line of divertor
Z = linspace(Z_Top, Z_Bottom);
REOR = ppval(spline(Z_EOR, R_EOR),Z);
AnglesEOR = ppval(spline(Z_EOR, Angle_EOR), Z);
Rinterm = ppval(spline(Z_interm, R_interm),Z);
Anglesinterm = ppval(spline(Z_interm, Angle_interm), Z);
REOD = ppval(spline(Z_EOD, R_EOD),Z);
AnglesEOD = ppval(spline(Z_EOD, Angle_EOD), Z);

% new basis based on the length on divertor surface
% recent version of MATLAB has 'arclength' function, but mine haven't it 
n = numel(Z);
XEOR = zeros(n, 1);
Xinterm = zeros(n, 1);
XEOD = zeros(n, 1);
for i = 1:n-1
  XEOR(i+1) = XEOR(i) + sqrt((Z(i+1)-Z(i))^2 + (REOR(i+1)-REOR(i))^2);
  Xinterm(i+1) = Xinterm(i) + sqrt((Z(i+1)-Z(i))^2 + (Rinterm(i+1)-Rinterm(i))^2); % simple Pythagoras
  XEOD(i+1) = XEOD(i) + sqrt((Z(i+1)-Z(i))^2 + (REOD(i+1)-REOD(i))^2);
end

tiledlayout(3,3)
% divertor geometry
nexttile; plot(Z_EOR, R_EOR,'o', Z, REOR,'r-'); title("EOR"); 
nexttile; plot(Z_interm, R_interm,'o', Z, Rinterm,'r-'); title("interm"); 
nexttile; plot(Z_EOD, R_EOD,'o', Z, REOD,'r-'); title("EOD"); 
% angle distribution on Z-axis (unit: Y=[degree], X=[m])
nexttile; plot(Z, AnglesEOR,'r-'); 
nexttile; plot(Z, Anglesinterm,'g-'); 
nexttile; plot(Z, AnglesEOD,'b-'); 
% angle trend from the bottom of inner divertor (unit: Y=[degree], X=[m])

nexttile; plot(XEOR, smooth(AnglesEOR,10),'r-'); hold on
            plot(Xinterm, smooth(Anglesinterm,10),'g-'); 
            plot(XEOD, smooth(AnglesEOD,10),'b-'); X=[0:0.05:1.677];
            title('angle')
            
            AnglesEOR=interp1(XEOR, AnglesEOR, X);
            Anglesinterm=interp1(Xinterm, Anglesinterm, X);
            AnglesEOD=interp1(XEOD, AnglesEOD, X);
            
            YEOR=1-sin((AnglesEOR)*pi/180)./sin((Anglesinterm)*pi/180);
            Yinterm=1-sin((Anglesinterm)*pi/180)./sin((Anglesinterm)*pi/180);
            YEOD=1-sin((AnglesEOD)*pi/180)./sin((Anglesinterm)*pi/180);
            
            YEOR=smooth(YEOR,10);
            Yinterm=smooth(Yinterm,10);
            YEOD=smooth(YEOD,10);
            
            for i=1:length(X)
                pf(i,:)=polyfit([0 1 2],[YEOR(i) Yinterm(i) YEOD(i)],1)
            end
%             pf(:,1)=(pf(:,1)-pf(:,2))/2;
%             pf(:,2)=-pf(:,1);
            
            for i=1:length(X)
                YEOR_fit(i)=0*pf(i,1)+pf(i,2);
                Yinterm_fit(i)=1*pf(i,1)+pf(i,2);
                YEOD_fit(i)=2*pf(i,1)+pf(i,2);
            end
                        
            plot(X, asin(sin(Anglesinterm*pi/180).*(1-YEOR_fit))*180/pi,'r:'); 
            plot(X, asin(sin(Anglesinterm*pi/180).*(1-Yinterm_fit))*180/pi,'g:'); 
            plot(X, asin(sin(Anglesinterm*pi/180).*(1-YEOD_fit))*180/pi,'b:'); hold off

nexttile; 
            plot(X, 1-YEOR,'r-'); hold on
            plot(X, 1-Yinterm,'g-');
            plot(X, 1-YEOD,'b-'); 
            title('sin(angle) relative to interm')
            
            plot(X, 1-YEOR_fit,'r:'); 
            plot(X, 1-Yinterm_fit,'g:'); 
            plot(X, 1-YEOD_fit,'b:'); hold off
            
nexttile;
            plot(X, pf(:,1),'c-'); hold on
            plot(X, pf(:,2),'m-'); hold off
            title('linear fit of relative sin(angle)')
            
            
            X=X';
            
            x_vals = [0.03488552708502455
                0.10040600153412998
                0.16100759702575432
                0.22094089328084088
                0.28109445910463104
                0.34617048684971735
                0.4112465145948036
                0.4714000804185942
                0.5308836728324285
                0.5905875348149668
                0.6507411006387576
                0.7158147281293848
                0.7918912083437122
                0.8850071376440829
                0.9842492134504772
                1.088480663943781
                1.2233499862333979
                1.3738107355006015
                1.5807020442642123
                ];
            
            coefficients_ = pf(:, 1);  % Slopes
            constants_ = pf(:, 2);     % Intercepts
            
            x_interpolated = interp1(X, X, x_vals, 'linear');
            
            coefficients = interp1(X, coefficients_, x_vals, 'linear');
            constants = interp1(X, constants_, x_vals, 'linear');

            y_vals = zeros(size(x_vals));
            
            for time = 0:160
                for i = 1:length(x_vals)
                    % Find the closest index in X to the interpolated x value
    %                 [~, idx] = min(abs(X - x_interpolated(i)));
                    % Use the slope and intercept from the corresponding segment
                    y_vals(i) = 1-polyval([coefficients(i) constants(i)], 2*time/160);
                end
                writematrix(y_vals,'angle_coeffs_t' + string(time) + '.txt', 'Delimiter',';');
            end
               

            % Display the interpolated y values
            disp('Interpolated y values:');
            disp(y_vals);            
            
            

            