function hfg = SW_LatentHeat(T,uT,S,uS)
    % SW_LatentHeat    Latent Heat of vaporization of seawater
    %=========================================================================
    % USAGE:  hfg = SW_LatentHeat(T,uT,S,uS)
    %
    % DESCRIPTION:
    %   Latent heat of vaporization of seawater using Eq. (37) given by [1].
    %   The pure water latent heat is a best fit to the data of [2].
    %   Values at temperature higher than the normal boiling temperature are
    %   calculated at the saturation pressure.
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
    %   hfg = Latent heat of vaporization [J/kg]
    %
    %   Note: hfg will have the same dimensions as T and S
    %
    % VALIDITY: 0 < T < 200 C; 0 < S < 240 g/kg
    %
    % ACCURACY: 0.01 %
    %
    % REVISION HISTORY:
    %   2009-12-18: Mostafa H. Sharqawy (mhamed@mit.edu), MIT
    %               - Initial version
    %   2012-06-06: Karan H. Mistry (mistry@alum.mit.edu), MIT
    %               - Allow T,S input in various units
    %               - Allow T,S to be matrices of any size
    %
    % DISCLAIMER:
    %   This software is provided "as is" without warranty of any kind.
    %   See the file sw_copy.m for conditions of use and licence.
    %
    % REFERENCES:
    %   [1] M. H. Sharqawy, J. H. Lienhard V, and S. M. Zubair, Desalination
    %       and Water Treatment, 16, 354-380, 2010. (http://web.mit.edu/seawater/)
    %   [3]	IAPWS release on the Thermodynamic properties of ordinary water substance, 1996.
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
    if ~isequal((T<0)+(T>200),zeros(size(T)))
        warning('Temperature is out of range for latent heat function 0<T<200 C');
    end

    if ~isequal((S<0)+(S>240),zeros(size(S)))
        warning('Salinity is out of range for latent heat function 0<S<240 g/kg');
    end

    %% BEGIN

    a = [
         2.5008991412E+06
        -2.3691806479E+03
         2.6776439436E-01
        -8.1027544602E-03
        -2.0799346624E-05
    ];

    hfg_w = a(1) + a(2)*T + a(3)*T.^2 + a(4)*T.^3 + a(5)*T.^4;
    hfg   = hfg_w.*(1-0.001*S);

end