function[PFlux,TCO,TEO,PFR,RhoF,CpF,RhoC,CpC,RhoP,AHvP]=...
    VAGMD_Models_NaCl(TEI_r,FFR_r,TCI_r,Sgl_r,Ttank_r,...
    FullModel_PFlux268,FullModel_TCO268,FullModel_TEO268,...
    FullModel_PFlux373,FullModel_TCO373,FullModel_TEO373,...
    FullModels_VarsPFlux268,FullModels_VarsTCO268,FullModels_VarsTEO268,...
    FullModels_VarsPFlux373,FullModels_VarsTCO373,FullModels_VarsTEO373,...
    FullModels_Coder,FullModels_CoderVars,k)

%% Models calculations.
syms TEI_c FFR_c TCI_c S_c
a1 = 0.983930048493388;
a2 = -4.8359231959954E-04;
S_r = a1 .* Sgl_r + a2 .* Sgl_r^2; % [g/kg].
if k == 7
    A = 7.2; % [m2].
    TEI_cv = subs(FullModels_CoderVars(1,:) * FullModels_Coder(:,1), TEI_r);
    FFR_cv = subs(FullModels_CoderVars(2,:) * FullModels_Coder(:,2), FFR_r);
    TCI_cv = subs(FullModels_CoderVars(3,:) * FullModels_Coder(:,3), TCI_r);
    S_cv =  subs(FullModels_CoderVars(4,:) * FullModels_Coder(:,4), S_r);
    PFlux = subs(FullModels_VarsPFlux268(1,:) * FullModel_PFlux268(:,1), {TEI_c FFR_c TCI_c S_c}, {TEI_cv FFR_cv TCI_cv S_cv}); % [kg/h/m2].
    TCO = subs(FullModels_VarsTCO268(1,:) * FullModel_TCO268(:,1), {TEI_c FFR_c TCI_c S_c}, {TEI_cv FFR_cv TCI_cv S_cv}); % [ºC].
    TEO = subs(FullModels_VarsTEO268(1,:) * FullModel_TEO268(:,1), {TEI_c FFR_c TCI_c S_c}, {TEI_cv FFR_cv TCI_cv S_cv}); % [ºC].
else
    A = 25.92; % [m2].
    TEI_cv = subs(FullModels_CoderVars(1,:) * FullModels_Coder(:,5), TEI_r);
    FFR_cv = subs(FullModels_CoderVars(2,:) * FullModels_Coder(:,6), FFR_r);
    TCI_cv = subs(FullModels_CoderVars(3,:) * FullModels_Coder(:,7), TCI_r);
    S_cv =  subs(FullModels_CoderVars(4,:) * FullModels_Coder(:,8), S_r);
    PFlux = subs(FullModels_VarsPFlux373(1,:) * FullModel_PFlux373(:,1), {TEI_c FFR_c TCI_c S_c}, {TEI_cv FFR_cv TCI_cv S_cv}); % [kg/h/m2].
    TCO = subs(FullModels_VarsTCO373(1,:) * FullModel_TCO373(:,1), {TEI_c FFR_c TCI_c S_c}, {TEI_cv FFR_cv TCI_cv S_cv}); % [ºC].
    TEO = subs(FullModels_VarsTEO373(1,:) * FullModel_TEO373(:,1), {TEI_c FFR_c TCI_c S_c}, {TEI_cv FFR_cv TCI_cv S_cv}); % [ºC].
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

%% Permeate flow rate (PFR) [kg/h].
PFR = PFlux .* A;