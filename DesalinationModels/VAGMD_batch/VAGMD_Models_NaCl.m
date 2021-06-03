function[PFlux,TCO,TEO,RhoF,CpF,RhoC,CpC,RhoP,AHvP,A]=...
   VAGMD_Models_NaCl(TEI_r,FFR_r,TCI_r,Sgl_r,Ttank_r,...
    FullModel_PFlux268_low,FullModel_TCO268_low,FullModel_TEO268_low,...
    FullModel_PFlux373_low,FullModel_TCO373_low,FullModel_TEO373_low,...
    FullModel_PFlux268_high,FullModel_TCO268_high,FullModel_TEO268_high,...
    FullModel_PFlux373_high,FullModel_TCO373_high,FullModel_TEO373_high,...
    FullModels_VarsPFlux268,FullModels_VarsTCO268,FullModels_VarsTEO268,...
    FullModels_VarsPFlux373,FullModels_VarsTCO373,FullModels_VarsTEO373,...
    FullModels_Coder,FullModels_CoderVars,k,Sf)

%% Models calculations.
syms TEI_c FFR_c TCI_c S_c
a1 = 0.983930048493388;
a2 = -4.8359231959954E-04;
S_r = a1 .* Sgl_r + a2 .* Sgl_r^2; % [g/kg].
if k == 7
    A = 7.2; % [m2].
    if Sf > 175.3
        PFlux = subs(FullModels_VarsPFlux268(1,:) * FullModel_PFlux268_high(:,1), {S_c}, {S_r}); % [kg/h/m2].
        TCO = subs(FullModels_VarsTCO268(1,:) * FullModel_TCO268_high(:,1), {S_c}, {S_r}); % [ºC].
        TEO = subs(FullModels_VarsTEO268(1,:) * FullModel_TEO268_high(:,1), {S_c}, {S_r}); % [ºC].
    else
        TEI_cv = subs(FullModels_CoderVars(1,:) * FullModels_Coder(:,1), TEI_r);
        FFR_cv = subs(FullModels_CoderVars(2,:) * FullModels_Coder(:,2), FFR_r);
        TCI_cv = subs(FullModels_CoderVars(3,:) * FullModels_Coder(:,3), TCI_r);
        S_cv =  subs(FullModels_CoderVars(4,:) * FullModels_Coder(:,4), S_r);
        PFlux = subs(FullModels_VarsPFlux268(1,:) * FullModel_PFlux268_low(:,1), {TEI_c FFR_c TCI_c S_c}, {TEI_cv FFR_cv TCI_cv S_cv}); % [kg/h/m2].
        TCO = subs(FullModels_VarsTCO268(1,:) * FullModel_TCO268_low(:,1), {TEI_c FFR_c TCI_c S_c}, {TEI_cv FFR_cv TCI_cv S_cv}); % [ºC].
        TEO = subs(FullModels_VarsTEO268(1,:) * FullModel_TEO268_low(:,1), {TEI_c FFR_c TCI_c S_c}, {TEI_cv FFR_cv TCI_cv S_cv}); % [ºC].
    end
else
    A = 25.92; % [m2].
    if Sf > 140.2
        PFlux = subs(FullModels_VarsPFlux373(1,:) * FullModel_PFlux373_high(:,1), {S_c}, {S_r}); % [kg/h/m2].
        TCO = subs(FullModels_VarsTCO373(1,:) * FullModel_TCO373_high(:,1), {S_c}, {S_r}); % [ºC].
        TEO = subs(FullModels_VarsTEO373(1,:) * FullModel_TEO373_high(:,1), {S_c}, {S_r}); % [ºC].
    else
        TEI_cv = subs(FullModels_CoderVars(1,:) * FullModels_Coder(:,5), TEI_r);
        FFR_cv = subs(FullModels_CoderVars(2,:) * FullModels_Coder(:,6), FFR_r);
        TCI_cv = subs(FullModels_CoderVars(3,:) * FullModels_Coder(:,7), TCI_r);
        S_cv =  subs(FullModels_CoderVars(4,:) * FullModels_Coder(:,8), S_r);
        PFlux = subs(FullModels_VarsPFlux373(1,:) * FullModel_PFlux373_low(:,1), {TEI_c FFR_c TCI_c S_c}, {TEI_cv FFR_cv TCI_cv S_cv}); % [kg/h/m2].
        TCO = subs(FullModels_VarsTCO373(1,:) * FullModel_TCO373_low(:,1), {TEI_c FFR_c TCI_c S_c}, {TEI_cv FFR_cv TCI_cv S_cv}); % [ºC].
        TEO = subs(FullModels_VarsTEO373(1,:) * FullModel_TEO373_low(:,1), {TEI_c FFR_c TCI_c S_c}, {TEI_cv FFR_cv TCI_cv S_cv}); % [ºC].
    end
end

%% Physical properties (Source: http://web.mit.edu/seawater).
P = 101325; % [Pa].
nullS = 0; % [g/kg].
RhoF = SW_Density(((TEI_r + double(TCO)) ./ 2),'c',S_r,'ppt',P,'pa'); % [kg/m3].
CpF = SW_SpcHeat(((TEI_r + double(TCO)) ./ 2),'c',S_r,'ppt',P,'pa'); % [J/kg/ºC].
RhoC = SW_Density(((TCI_r + Ttank_r) ./ 2),'c',nullS,'ppt',P,'pa'); % [kg/m3].
CpC = SW_SpcHeat(((TCI_r + Ttank_r) ./ 2),'c',nullS,'ppt',P,'pa'); % [J/kg/ºC].
RhoP = SW_Density(((TCI_r + double(TCO)) ./ 2),'c',nullS,'ppt',P,'pa'); % [kg/m3].
AHvP = SW_LatentHeat(((TCI_r + double(TCO)) ./ 2),'c',nullS,'ppt'); % [J/kg].