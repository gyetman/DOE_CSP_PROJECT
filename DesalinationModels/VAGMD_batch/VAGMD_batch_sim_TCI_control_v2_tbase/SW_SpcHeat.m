function cp = SW_SpcHeat(T,uT,S,uS,P,uP)
    % SW_SpcHeat    Specific heat at constant pressure of seawater
    %=========================================================================
    % USAGE:  cp = SW_SpcHeat(T,uT,S,uS,P,uP)
    %
    % DESCRIPTION:
    %   Specific heat capacity of seawater at 0.1 MPa given by [1]
    %   Calculation for non-atmospheric pressures (P_sat < P < 12 MPa)
    %   given in [2]
    %
    % INPUT:
    %   T  = temperature
    %   uT = temperature unit
    %        'C'  : [degree Celsius] (ITS-90)
    %        'K'  : [Kelvin]
    %        'F'  : [degree Fahrenheit]
    %        'R'  : [Rankine]
    %   S  = salinity
    %   uS = salinity unit
    %        'ppt': [g/kg]  (reference-composition salinity)
    %        'ppm': [mg/kg] (in parts per million)
    %        'w'  : [kg/kg] (mass fraction)
    %        '%'  : [kg/kg] (in parts per hundred)
    %   P  = pressure
    %   uP = pressure unit
    %        'MPa': [MPa]
    %        'bar': [bar]
    %        'kPa': [kPa]
    %        'Pa' : [Pa]
    %
    %   Note: T, S and P must have the same dimensions        %
    %
    % OUTPUT:
    %   cp = specific heat [J/kg-K]
    %
    %   Note: cp will have the same dimensions as T, S and P
    %
    % VALIDITY: (1) 0 < T < 180 C; 0 < S < 180 g/kg; 0.1 < P = P0 < 1 MPa
    %           (2) 0 < T < 180 C; S = 0 g/kg; 0 < P < 12 MPa
    %           (3) 0 < T < 40 C; 0 < S < 42 g/kg; 0 < P < 12 MPa
    %           (4) 40 < T < 180 C; 0 < S < 42 g/kg; 0 < P < 12 MPa
    %           (5) 0 < T < 180 C; 42 < S < 180 g/kg; 0 < P < 12 MPa

    % ACCURACY: (1) 1%
    %           (2) 1%
    %           (3) 1%
    %           (4) 1% (Extrapolated)
    %           (5) 1% (Extrapolated)
    %
    % REVISION HISTORY:
    %   2009-12-18: Mostafa H. Sharqawy (mhamed@mit.edu), MIT
    %               - Initial version
    %   2012-06-06: Karan H. Mistry (mistry@alum.mit.edu), MIT
    %               - Allow T,S input in various units
    %               - Allow T,S to be matrices of any size
    %   2015-04-15: Kishor G. Nayar (kgnayar@mit.edu), MIT
    %               - Extended function to 12 MPa; corrected salinity to
    %                 "Reference salinity" from "Salinity Product"
    %   2016-04-10: Karan H. Mistry (mistry@alum.mit.edu), MIT
    %               - Allow T,S to be matrices of any size
    %
    % DISCLAIMER:
    %   This software is provided "as is" without warranty of any kind.
    %   See the file sw_copy.m for conditions of use and licence.
    %
    % REFERENCES:
    % [1] D. T. Jamieson, J. S. Tudhope, R. Morris, and G. Cartwright,
    %      Desalination, 7(1), 23-30, 1969.
    % [2]  K.G. Nayar, M. H. Sharqawy, L.D. Banchik and J. H. Lienhard V, Desalination,
    %       390, 1-24, 2016. (http://web.mit.edu/seawater/) 
    %=========================================================================

     %% CHECK INPUT ARGUMENTS

    % CHECK THAT S,T&P HAVE SAME SHAPE
    if ~isequal(size(S),size(T),size(P))
        error('check_stp: S, T & P must have same dimensions');
    end


     % CONVERT TEMPERATURE INPUT TO °C
     switch lower(uT)
         case 'c'
         case 'k'
             T = T - 273.15;
         case 'f'
             T = 5/9*(T-32);
         case 'r'
             T = 5/9*(T-491.67);
         otherwise
             error('Not a recognized temperature unit. Please use ''C'', ''K'', ''F'', or ''R''');
     end

     % CONVERT SALINITY TO PPT
     switch lower(uS)
         case 'ppt'
         case 'ppm'
             S = S/1000;
         case 'w'
             S = S*1000;
         case '%'
             S = S*10;
         otherwise
             error('Not a recognized salinity unit. Please use ''ppt'', ''ppm'', ''w'', or ''%''');
     end

     % CONVERT PRESSURE INPUT TO MPa
    switch lower(uP)
        case 'mpa'
        case 'bar'
            P = P/10;
        case 'kpa'
            P = P/1000;
        case 'pa'
            P = P/1E6;
        otherwise
            error('Not a recognized pressure unit. Please use ''MPa'', ''bar'', ''kPa'', or ''Pa''');
    end

    % CHECK THAT S, T & P ARE WITHIN THE FUNCTION RANGE
    if ~isequal((T<0)+(T>180),zeros(size(T)))
        warning('Temperature is out of range for specific heat function 0<T<180 C');
    end

    if ~isequal((S<0)+(S>180),zeros(size(S)))
        warning('Salinity is out of range for specific heat function 0<S<180 g/kg');
    end

    Psat = SW_Psat(T,'C',S,'ppt')/1E6;

    if ~isequal((P<Psat)+(Psat>12),zeros(size(P)))
        warning('Pressure is out of range for specific heat function P_sat < P < 12 MPa');
    end

    %% BEGIN

    P0 = Psat;
    P0(find(T<100)) = 0.101325;

    T68 = 1.00024*(T+273.15);      %convert from T_90 to T_68

    S_gkg=S;

    A = 5.328 - 9.76 * 10 ^ (-2) * S + 4.04*10^(-4)*(S).^ 2;
    B = -6.913 * 10 ^ (-3) + 7.351 * 10 ^ (-4) * (S) - 3.15*10^(-6)*(S).^2;
    C = 9.6 * 10 ^ (-6) - 1.927 * 10 ^ (-6) * (S) + 8.23 * 10^(-9) *(S).^2;
    D = 2.5 * 10 ^ (-9) + 1.666 * 10 ^ (-9) * (S) - 7.125 * 10^(-12)*(S).^2;
    cp_sw_P0 = 1000.*(A + B.*T68 + C.*(T68.^2) + D.*(T68.^3));

    % Pressure dependent terms; T_90 in °C and S in g/kg
    c1 = -3.1118;
    c2 = 0.0157;
    c3 = 5.1014 * 10 ^ (-5);
    c4 = -1.0302 * 10 ^ (-6);
    c5 = 0.0107;
    c6 = -3.9716 * 10 ^ (-5);
    c7 = 3.2088 * 10 ^ (-8);
    c8 = 1.0119 * 10 ^ (-9);

    cp_sw_P = (P - P0).*(c1 + c2*T + c3*(T.^2) + c4*(T.^3) + S_gkg.*(c5 + c6*T + c7*(T.^2) + c8*(T.^3)));

    cp = cp_sw_P0 + cp_sw_P;
end