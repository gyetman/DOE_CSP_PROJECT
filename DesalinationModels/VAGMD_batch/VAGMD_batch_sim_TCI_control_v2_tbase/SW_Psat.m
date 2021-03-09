function Pv = SW_Psat(T,uT,S,uS)
    % SW_Psat    Saturation (vapor) pressure of seawater
    %=========================================================================
    % USAGE:  Pv = SW_Psat(T,uT,S,uS)
    %
    % DESCRIPTION:
    %   Vapor pressure of natural seawater given by [1] based on new correlation
    %   The pure water vapor pressure is given by [2]
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
    %
    %   Note: T and S must have the same dimensions
    %
    % OUTPUT:
    %   Pv = vapor pressure [N/m^2]
    %
    %   Note: Pv will have the same dimensions as T and S
    %
    % VALIDITY: (1) 20 < T < 180 C; 0 < S < 180 g/kg
    %           (2)  0 < T <  20 C; 0 < S < 180 g/kg
    %
    % ACCURACY: (1) 0.26%
    %           (2) 0.91%
    %
    % REVISION HISTORY:
    %   2009-12-18: Mostafa H. Sharqawy (mhamed@mit.edu), MIT
    %               - Initial version based on correlation from [3]
    %   2012-06-06: Karan H. Mistry (mistry@alum.mit.edu), MIT
    %               - Allow T,S input in various units
    %               - Allow T,S to be matrices of any size
    %   2014-07-30: Kishor G. Nayar (kgnayar@mit.edu), MIT
    %               - Revised version with new correlation
    %
    % DISCLAIMER:
    %   This software is provided "as is" without warranty of any kind.
    %   See the file sw_copy.m for conditions of use and licence.
    %
    % REFERENCES:
    %   [1] K.G. Nayar, M. H. Sharqawy, L.D. Banchik and J. H. Lienhard V, Desalination,
    %       390, 1-24, 2016. (http://web.mit.edu/seawater/) 
    %   [2]  ASHRAE handbook: Fundamentals, ASHRAE; 2005.
    %   [3] M. H. Sharqawy, J. H. Lienhard V, and S. M. Zubair, Desalination
    %       and Water Treatment, 16, 354-380, 2010. (http://web.mit.edu/seawater/)
    %=========================================================================

    %% CHECK INPUT ARGUMENTS

    % CHECK THAT S&T HAVE SAME SHAPE
    if ~isequal(size(S),size(T))
        error('check_stp: S & T must have same dimensions');
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

    % CHECK THAT S & T ARE WITHIN THE FUNCTION RANGE
    if ~isequal((T<0)+(T>180),zeros(size(T)))
        warning('Temperature is out of range for vapor pressure function 0<T<180 C');
    end

    if ~isequal((S<0)+(S>180),zeros(size(S)))
        warning('Salinity is out of range for vapor pressure function 0<S<180 g/kg');
    end

    %% BEGIN

    T = T + 273.15;

    a = [
        -5.8002206E+03
         1.3914993E+00
        -4.8640239E-02
         4.1764768E-05
        -1.4452093E-08
         6.5459673E+00
    ];

    Pv_w = exp((a(1)./T) + a(2) + a(3)*T + a(4)*T.^2 + a(5)*T.^3 + a(6)*log(T));

    b  = [
        -4.5818 * 10 ^ -4
        -2.0443 * 10 ^ -6
    ];

    Pv   = Pv_w.*exp(b(1)*S+b(2)*S.^2);
end