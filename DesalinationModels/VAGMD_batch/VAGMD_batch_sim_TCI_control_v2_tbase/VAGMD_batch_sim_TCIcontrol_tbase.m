%% AS7C1.5L(268) AND AS26C2.7L(373) BATCH V-AGMD SIMULATION

% Assumptions:
% - Ranges of validity of the model:
%   - Input variables (factors):
%       - Evaporation channels inlet temperature (TEI_r): 60 <= TEI_r <= 80 [degC].
%       - Cooling channels inlet temperature (TCI_r): 20 <= TCI_r <= 30 [degC].
%       - Feed flow rate (FFR_r): 400 <= FFR_r <= 1100 [l/h].
%       - Feed salinity (S_r): 35 <= S_r <= 175.3 [g/l] (for AS7C1.5L(268)),
%                              35 <= S_r <= 105 [g/l] (for AS26C2.7L(373)).
%   - Output variables (responses):
%       - Permeate flux (PFlux) [kg/h/m2].
%       - Cooling channels outlet temperature (TCO) [degC].
%       - Evaporation channels outlet temperature (TEO) [degC].                   
% - TEI, FFR, and TCI are constant during all the simulation.
% - The feed tank is ideally mixed.
% - Negligible variation of the volume in the feed tank due to leak through the membrane pores.

% Title.
fprintf('\n\n Simulation of batch operation');
fprintf('\n -----------------------------\n');
fprintf('\n Please provide the following information:\n\n');

% Module selection.
k = 1;
disp(' - The module you would like to analyze. Two options are possible:');
disp('   - Module AS7C1.5L(268), which yields maximum permeate productivity.');
disp('     * 7.20 m2 membrane area.');
disp('     * 6 internal envelopes, that delimit 6 evaporation channels and 6 cooling channels.');
disp('     * 1.5 m channels length.');
disp('   - Module AS26C2.7L(373), which yields maximum thermal efficiency.');
disp('     * 25.92 m2 membrane area.');
disp('     * 12 internal envelopes, that delimit 12 evaporation channels and 12 cooling channels.');
disp('     * 2.7 m channels length.');
while (k ~= 7) && (k ~= 26)
    k = input('\n - Enter "7" if AS7C1.5L(268), or "26" if AS26C2.7L(373): ');
    if (k ~= 7) && (k ~= 26)
        fprintf('   Incorrect value. Please provide a valid one.\n\n');
    end
end

% Constants.
Vdisch = 3.2175; % [l].
minS = 35; % [g/l].
if k == 7
    maxS = 175.3; % [g/l].
else
    maxS = 105; % [g/l].
end
maxRR = 100*(1-(minS/maxS)); % [%] Given by the range of feed salinities in which the models were developed.

% Initial conditions (chosen by the user):
i = 1;
S0 = 400; RR = 200; Vmin = 5; dt = -1;  V0 = 0; TEI(i,1) = 0; FFR(i,1) = 0; TCI(i,1) = 0;  % Flags for accessing the while loops.
if k == 7
    while (S0 >= maxS) || (S0 < minS)
        S0 = input(' - A valid value of initial feed salinity (S0) in g/l (between 35 and 175.3): ');
        if (S0 >= maxS) || (S0 < minS)
            fprintf('   The value of S0 is not in the range allowed by the model. Please provide a valid one.\n\n');
        end
    end
    RRf = 100*(1-(S0/maxS)); % [%].
    fprintf('\n   The maximum value of final recovery ratio (RRf) allowed by the model is %2.2f %%.\n\n',round(RRf-sign(RRf)*0.5/10^2,2));
    while (RR > RRf) || (RR <= 0)
        RR = input(' - A valid value of RR in % (between 0 and the maximum): ');    
        if (RR > RRf) || (RR <= 0)
            fprintf('   The value of RR is higher than the allowed by the model (%2.2f %%), negative or zero.\n   Please provide a value in range.\n\n',round(RRf-sign(RRf)*0.5/10^2,2));
        end
    end
else
    while (S0 >= maxS) || (S0 < minS)
        S0 = input(' - A valid value of initial feed salinity (S0) in g/l (between 35 and 105): ');
        if (S0 >= maxS) || (S0 < minS)
            fprintf('   The value of S0 is not in the range allowed by the model. Please provide a valid one.\n\n');
        end
    end
    RRf = 100*(1-(S0/maxS)); % [%].
    fprintf('\n   The maximum value of final recovery ratio (RRf) allowed by the model is %2.2f %%.\n\n',round(RRf-sign(RRf)*0.5/10^2,2));
    while (RR > RRf) || (RR <= 0)
        RR = input(' - A valid value of RR in % (between 0 and the maximum): ');    
        if (RR > RRf) || (RR <= 0)
            fprintf('   The value of RR is higher than the allowed by the model (%2.2f %%), negative or zero.\n   Please provide a value in range.\n\n',round(RRf-sign(RRf)*0.5/10^2,2));
        end
    end
end
Sf = (S0)./(1-(RR/100)); % [g/l].
fprintf('\n   The final feed salinity (Sf) will be around %2.1f g/l.\n\n',Sf);
while dt <= 0
    dt = input(' - A valid value of time increment (dt) in s: ');
    if dt <= 0
        fprintf('   The value of dt must be positive. Please provide a valid one.\n\n');
    end
end
while V0 <= Vmin
    V0 = input(' - A valid value of initial batch volume (V0) in l: ');
    if V0 <= Vmin
        fprintf('   The value of V0 is less than %1.0f l. Please provide a valid one.\n\n',Vmin);
    end
end
while (TEI < 60) || (TEI > 80)
    TEI(i,1) = input(' - A valid value of evaporation channels inlet temperature (TEI) in degC (between 60 and 80): ');
    if (TEI < 60) || (TEI > 80)
        fprintf('   The value of TEI is out of range. Please provide a valid one.\n\n');
    end
end
while (FFR < 400) || (FFR > 1100)
    FFR(i,1) = input(' - A valid value of feed flow rate (FFR) in l/h (between 400 and 1100): ');
    if (FFR < 400) || (FFR > 1100)
        fprintf('   The value of FFR is out of range. Please provide a valid one.\n\n');
    end
end
while (TCI < 20) || (TCI > 30)
    TCI(i,1) = input(' - A valid value of cooling channels inlet temperature (TCI) in degC (between 20 and 30): ');
    if (TCI < 20) || (TCI > 30)
        fprintf('   The value of TCI is out of range. Please provide a valid one.\n\n');
    end
end
fprintf('\n Please wait for some seconds...\n');

% Calculations. 
load VAGMD_Models_NaCl.mat
Ttank(i,1) = TCI(i,1); % [degC].
[PFlux_c,TCO_c,TEO_c,PFR_c,RhoF,CpF,RhoC,CpC,~,~] =...
    VAGMD_Models_NaCl(TEI(i,1),FFR(i,1),TCI(i,1),S0,Ttank(i,1),...
    FullModel_PFlux268,FullModel_TCO268,FullModel_TEO268,...
    FullModel_PFlux373,FullModel_TCO373,FullModel_TEO373,...
    FullModels_VarsPFlux268,FullModels_VarsTCO268,FullModels_VarsTEO268,...
    FullModels_VarsPFlux373,FullModels_VarsTCO373,FullModels_VarsTEO373,...
    FullModels_Coder,FullModels_CoderVars,k);
PFlux(i,1) = double(PFlux_c); % [kg/h/m2].
PFR(i,1) = double(PFR_c); % [kg/h].
V(i,1) = V0; % [l].
Vd(i,1) = V0 - V(i,1); % [l].
AccVd(i,1) = 0; % [l].
t(i,1) = 0; % [h].
tminute(i,1) = t(i,1).*60; % [h].
RR(i,1) = 0; % [%].
S(i,1) = S0; % [g/l].
TCO(i,1) = double(TCO_c); % [degC].
TEO(i,1) = double(TEO_c); % [degC].
ATml(i,1) = ((TEI(i,1)-TCO(i,1))-(TEO(i,1)-TCI(i,1))) ./ (log((TEI(i,1)-TCO(i,1))./(TEO(i,1)-TCI(i,1)))); % [degC].
ThPower(i,1) = (FFR(i,1).*CpF.*(TEI(i,1)-TCO(i,1))) .* (RhoF./(1000.* 3600.*1000)); % [kWth].
ThEnergy(i,1) = 0; % [kWhth].
AccThEnergy(i,1) = 0; % [kWhth].
CPower(i,1) = (FFR(i,1).*CpC.*(Ttank(i,1)-TCI(i,1))).*(RhoC/(1000.*3600.*1000)); % [kWth].
CEnergy(i,1) = 0; % [kWhth].
AccCEnergy(i,1) = 0; % [kWhth].
STEC(i,1) = 0; % [kWhth/m3].
GOR(i,1) = 0; % [-].

while S(i,1) < Sf
    i = i+1;
    t(i,1) = t(i-1,1)+(dt./3600); % [h].
    tminute(i,1) = t(i,1).*60; % [min].
    Vd(i,1) = PFR(i-1,1) .* (t(i,1)-t(i-1,1)); % [l].
    V(i,1) = V(i-1,1) - Vd(i,1); % [l].
    TEI(i,1) = TEI(i-1,1); % [degC].
    FFR(i,1) = FFR(i-1,1); % [l/h].
    TCI(i,1) = TCI(i-1,1); % [degC].
    S(i,1) = (V(i-1,1)./V(i,1)).*S(i-1,1); % [g/l].
    Ttank(i,1) = vpa((((FFR(i-1,1).*(t(i,1)-t(i-1,1)).*TEO(i-1,1))+(V(i-1,1).*TCI(i-1,1)))/((V(i-1,1))+(FFR(i-1,1).*(t(i,1)-t(i-1,1))))),3); % [degC].
    [PFlux_c,TCO_c,TEO_c,PFR_c,RhoF,CpF,RhoC,CpC,RhoP,AHvP] =...
        VAGMD_Models_NaCl(TEI(i,1),FFR(i,1),TCI(i,1),S(i,1),Ttank(i,1),...
        FullModel_PFlux268,FullModel_TCO268,FullModel_TEO268,...
        FullModel_PFlux373,FullModel_TCO373,FullModel_TEO373,...
        FullModels_VarsPFlux268,FullModels_VarsTCO268,FullModels_VarsTEO268,...
        FullModels_VarsPFlux373,FullModels_VarsTCO373,FullModels_VarsTEO373,...
        FullModels_Coder,FullModels_CoderVars,k);
    PFlux(i,1) = double(PFlux_c); % [kg/h/m2].
    PFR(i,1) = double(PFR_c); % [kg/h].
    AccVd(i,1) = Vd(i,1) + AccVd(i-1,1); % [l].
    RR(i,1) = 100.*(1-(S0./S(i))); % [%].
    TCO(i,1) = double(TCO_c); % [degC].
    TEO(i,1) = double(TEO_c); % [degC].
    ATml(i,1) = ((TEI(i,1)-TCO(i,1))-(TEO(i,1)-TCI(i,1))) ./ (log((TEI(i,1)-TCO(i,1))./(TEO(i,1)-TCI(i,1)))); % [degC].
    ThPower(i,1) = (FFR(i,1).*CpF.*(TEI(i,1)-TCO(i,1))) .* (RhoF./(1000.* 3600.*1000)); % [kWth].
    ThEnergy(i,1) = ThPower(i-1,1).*(t(i,1)-t(i-1,1)); % [kWhth].
    AccThEnergy(i,1) = ThEnergy(i,1) + AccThEnergy(i-1,1); % [kWhth].
    CPower(i,1) = (FFR(i,1).*CpC.*(Ttank(i,1)-TCI(i,1))).*(RhoC/(1000.*3600.*1000)); % [kWth].
    CEnergy(i,1) = CPower(i-1,1).*(t(i,1)-t(i-1,1)); % [kWhth].
    AccCEnergy(i,1) = CEnergy(i,1)+AccCEnergy(i-1,1); % [kWhth].
    STEC(i,1) = AccThEnergy(i,1)./(AccVd(i,1)./1000); % [kWhth/m3].
    GOR(i,1) = (AccVd(i,1).*AHvP.*RhoP./1000)/(AccThEnergy(i,1).*3.6e6); % [-].
end
Results = table(t,tminute,V,Vd,AccVd,TEI,FFR,TCI,S,PFR,PFlux,RR,TCO,TEO,Ttank,ATml,ThPower,ThEnergy,AccThEnergy,...
    CPower,CEnergy,AccCEnergy,STEC,GOR)
fprintf('\n\n End of simulation.\n\n\n');
clear FullModel_PFlux268 FullModel_PFlux373 FullModel_TCO268 FullModel_TCO373 FullModel_TEO268 FullModel_TEO373...
    FullModels_Coder FullModels_CoderVars FullModels_VarsPFlux268 FullModels_VarsPFlux373 FullModels_VarsTCO268...
    FullModels_VarsTCO373 FullModels_VarsTEO268 FullModels_VarsTEO373 PFlux_c TCO_c TEO_c PFR_c RhoP AHvP RhoC CpC RhoF CpF i k