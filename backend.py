#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
QSDsan-webapp: Web application for QSDsan

This module is developed by:
    
    Yalin Li <mailto.yalin.li@gmail.com>

This module is under the University of Illinois/NCSA Open Source License.
Please refer to https://github.com/QSD-Group/QSDsan/blob/main/LICENSE.txt
for license details.
'''

import biosteam as bst
from Bioindustrial_Park.biorefineries.cellulosic import Biorefinery as CellulosicEthanol
from Bioindustrial_Park.biorefineries.cellulosic import Biorefinery as CellulosicEthanol
from Bioindustrial_Park.biorefineries.cellulosic.streams import cornstover as cornstover_kwargs
from Bioindustrial_Park.biorefineries.cornstover import ethanol_density_kggal

def calculate_ethanol_price_GWP(mass):
    """
    mass: float, kg/hr
    For the calculation
    """
    
    br = CellulosicEthanol(
        name='ethanol',
        )

    sys = br.sys # system
    tea = sys.TEA # Techno-economic analysis
    f = sys.flowsheet # flowsheet
    stream = f.stream # stream
    feedstock = stream.cornstover # feedstock
    ethanol = stream.ethanol # ethanol

    feedstock.F_mass = mass # kg/hr 

    prices = {
        'cornstover': 0.2, # $/kg including water
        }
    for ID, price in prices.items(): stream.search(ID).price = price
    bst.PowerUtility.price = 0.07

    GWP_CFs = {
        'cornstover': 0.2,
        'sulfuric_acid': 1,
        'ammonia': 1,
        'cellulase': 1, 
        'CSL': 1,
        'caustic': 1, 
        'FGD_lime': 1, 
        }
    for ID, CF in GWP_CFs.items(): stream.search(ID).characterization_factors['GWP'] = CF
    bst.PowerUtility.characterization_factors['GWP'] = (1., 1.,) # consumption, production

    sys.simulate()
    get_ethanol = lambda: ethanol.F_mass*ethanol_density_kggal*tea.operating_hours/1e6 # MM gal/year
    get_MESP = lambda: tea.solve_price(ethanol)*ethanol_density_kggal # from $/kg to $/gallon
    get_GWP = lambda: sys.get_net_impact('GWP')/sys.operating_hours/ethanol.F_mass*ethanol_density_kggal

    print(f'annual ethanol: ${get_ethanol():.3f} MM gal/yr')
    print(f'price: ${get_MESP():.2f}/gal')
    print(f'GWP: {get_GWP():.2f} kg CO2e/gal')
    
if __name__ == "__main__":
    calculate_ethanol_price_GWP(1000) # kg/hr
