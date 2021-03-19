function rho = SW_Density(T,uT,S,uS,P,uP)
    % SW_Density    Density of seawater
    %=========================================================================
    % USAGE:  rho = SW_Density(T,uT,S,uS,P,uP)
    %
    % DESCRIPTION:
    %   Density of seawater at atmospheric pressure (0.1 MPa) using Eq. (8)
    %   given by [1] which best fit the data of [2] and [3]. The pure water
    %   density equation is a best fit to the data of [4].
    %   Density at non-atmospheric pressures (P_sat < P < 12 MPa) is from
    %   [5] with the original calculation based on isothermal compressibility
    %   data from [6]
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
    %   uS = pressure unit
    %        'MPa': [MPa]
    %        'bar': [bar]
    %        'kPa': [kPa]
    %        'Pa' : [Pa]
    %
    %   Note: T, S and P must have the same dimensions        %
    %
    % OUTPUT:
    %   rho = density [kg/m^3]
    %
    %   Note: rho will have the same dimensions as T and S
    %
    % VALIDITY: (1) 0 < T < 180 C; 0 < S < 180 g/kg; 0.1 < P = P0 < 1 MPa
    %           (2) 0 < T < 180 C; 0 < S < 56 g/kg; P_sat < P < 12 MPa
    %           (3) 0 < T < 180 C; 56 < S < 180 g/kg; P_sat < P < 12 MPa
    %
    % ACCURACY: (1) 0.14%
    %           (2) 0.14%
    %           (3) 0.21% (Extrapolation)
    %
    %
    % REVISION HISTORY:
    %   2009-12-18: Mostafa H. Sharqawy (mhamed@mit.edu), MIT
    %               - Initial version
    %   2012-06-06: Karan H. Mistry (mistry@alum.mit.edu), MIT
    %               - Allow T,S input in various units
    %               - Allow T,S to be matrices of any size
    %   2009-12-18: Mostafa H. Sharqawy (mhamed@mit.edu), MIT
    %               - Initial version
    %   2014-09-20: Kishor G. Nayar (kgnayar@mit.edu), MIT
    %               - Extended function to 12 MPa
    %   2016-04-10: Karan H. Mistry (mistry@alum.mit.edu), MIT
    %               - Allow T,S to be matrices of any size
    %
    % DISCLAIMER:
    %   This software is provided "as is" without warranty of any kind.
    %   See the file sw_copy.m for conditions of use and license.
    %
    % REFERENCES:
    %   [1] M. H. Sharqawy, J. H. Lienhard V, and S. M. Zubair, Desalination
    %       and Water Treatment, 16, 354-380, 2010. (http://web.mit.edu/seawater/)
    %   [2] Isdale, and Morris, Desalination, 10(4), 329-339, 1972.
    %   [3] Millero and Poisson, Deep-Sea Research, 28A (6), 625, 1981
    %   [4] IAPWS release on the Thermodynamic properties of ordinary water substance, 1996.
    %   [5] K.G. Nayar, M. H. Sharqawy, L.D. Banchik and J. H. Lienhard V, Desalination,
    %       390, 1-24, 2016. (http://web.mit.edu/seawater/) 
    %   [6] J. Safarov, S. Berndt, F. Millero, R. Feistel, A. Heintz and E. Hassel, Deep Sea Res.
    %       Part I Oceanogr. Res. Pap., 65, 2012
    %=========================================================================

    %% CHECK INPUT ARGUMENTS
    %
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

    % CHECK THAT S & T ARE WITHIN THE FUNCTION RANGE
    if ~isequal((T<0)+(T>180),zeros(size(T)))
        warning('Temperature is out of range for density function 0 < T < 180 C');
    end

    if ~isequal((S<0)+(S>180),zeros(size(S)))
        warning('Salinity is out of range for density function 0 < S < 180 g/kg');
    end

    Psat = SW_Psat(T,'C',S,'ppt')/1E6;

    if ~isequal((P<Psat)+(Psat>12),zeros(size(P)))
        warning('Pressure is out of range for density function P_sat < P < 12 MPa');
    end


    %% BEGIN

    P0 = Psat;
    P0(find(T<100)) = 0.101325;

    s = S/1000;

    a = [
         9.9992293295E+02
         2.0341179217E-02
        -6.1624591598E-03
         2.2614664708E-05
        -4.6570659168E-08
    ];

    b = [
         8.0200240891E+02
        -2.0005183488E+00
         1.6771024982E-02
        -3.0600536746E-05
        -1.6132224742E-05
    ];

    rho_w = a(1) + a(2)*T + a(3)*T.^2 + a(4)*T.^3 + a(5)*T.^4;
    D_rho = b(1)*s + b(2)*s.*T + b(3)*s.*T.^2 + b(4)*s.*T.^3 + b(5)*s.^2.*T.^2;
    rho_sw_sharq   = rho_w + D_rho;


    c = [
         5.0792E-04
        -3.4168E-06
         5.6931E-08
        -3.7263E-10
         1.4465E-12
        -1.7058E-15
        -1.3389E-06
         4.8603E-09
        -6.8039E-13
    ];


    d=[
        -1.1077e-06
         5.5584e-09
        -4.2539e-11
         8.3702e-09
       ];


    kT =    c(1) + c(2)*T + c(3)*T.^2 + c(4)*T.^3 + c(5)*T.^4 + c(6)*T.^5 + ...
        P.*(c(7) + c(8)*T + c(9)*T.^3) + ...
        S.*(d(1) + d(2)*T + d(3)*T.^2 + d(4)*P);

    F_P = exp( (P-P0).*(c(1) + c(2)*T + c(3)*T.^2 + c(4)*T.^3 + c(5)*T.^4 + c(6)*T.^5 + S.*(d(1) + d(2)*T + d(3)*T.^2)) + ...
        0.5*(P.^2-P0.^2).*(c(7) + c(8)*T + c(9)*T.^3   + d(4)*S));

    rho = rho_sw_sharq.*F_P;


end