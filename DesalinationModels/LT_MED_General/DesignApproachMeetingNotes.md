<u><b> Zoom Meeting with PSA, 9/11/2019 </u></b>

Looking at the anticipated MED model inputs, PSA recommends not to let the user adjust tube bundle dimensions. Rather, the user should be
able to enter the MED production capacity and be able to add effects. Prof. Fthenakis also says we should focus on a desalination-design-centric
approach, where the user first enters the daily production capacity of the plant. Adam mentioned that we can have two approaches:
i) Solar Thermal System Driven- start with design of a solar technology and use those outputs to determine what the MED plant capacity, GOR, and
other design parameters would be.
ii) Desalination System Driven- start with design of a desal technology, specifying nominal water production.

Right now, our codes follow the first mode of design: Solar thermal system driven design.

(Diego&Patrica: Number of preheaters is defined once selecting number of effects; number of preheaters= number of effects minus 1)

MD
We have the permeate gap (first one sent) w/empirical equations sent by email (Solarspring module). Second model sent was vacuum-enhanced airgap MD. Guillermo will send another MD model on MEMSYS module.

Condenser channel inlet temp = feedwater temp
evaporator channel inlet temp --> determined by solar heat provision, but can enter as input

feedflow rate- main cost is energy
Tradeoff between energy efficiency and permeate flux

Condenser channel outlet temperature: might not be a useful output (this is essentially the evaporator channel inlet). Sounds more like an 
intermediate, internal calculation.

Question- empirical equations for determining thermal load? 

PSA will need to resend MD model. The membrane area is 25.9 m^2, not 24 m^2.

<u>MED configurations</u>
The TVC-MED model is written in EES. We can make an empirical model in Python and compare its results with those of the detailed EES model to assess error. We only have the EES model from PSA. Work needed to create empirical model in Python. Diego and Zhuoran developed empirical equations in June 2019.

MED w/Absorption heat pump: Diego has a model in EES so we would need to translate that. 

Solar thermal models require more sophisticated algorithms for irradiance over sloped surfaces. This is something we need to decide
concerning the static collectors.
