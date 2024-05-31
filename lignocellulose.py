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
from Bioindustrial_Park.biorefineries.cellulosic.streams import cornstover as cornstover_kwargs
from Bioindustrial_Park.biorefineries.cornstover import ethanol_density_kggal


br = CellulosicEthanol(
    name='ethanol',
    )

sys = br.sys
tea = sys.TEA
f = sys.flowsheet
stream = f.stream
feedstock = stream.cornstover
ethanol = stream.ethanol

#!!! Need to update the composition, etc.
# here's what `cornstover_kwargs` looks like
# cornstover = stream_kwargs(
#     'cornstover',
#     Glucan=0.28,
#     Xylan=0.1562,
#     Galactan=0.001144,
#     Arabinan=0.01904,
#     Mannan=0.0048,
#     Lignin=0.12608,
#     Acetate=0.01448,
#     Protein=0.0248,
#     Extract=0.1172,
#     Ash=0.03944,
#     Sucrose=0.00616,
#     Water=0.2,
#     total_flow=104229.16,
#     units='kg/hr',
#     price=0.05158816935126135,
# )

feedstock.F_mass = 1000 # kg/hr

#!!! Needs updating, put the baseline values here, current numbers are placeholders
prices = {
    'cornstover': 0.2, # $/kg including water
    }
for ID, price in prices.items(): stream.search(ID).price = price
bst.PowerUtility.price = 0.07

GWP_CFs = {
    'cornstover': 0.2,
    'sulfuric_acid': 1,
    'ammonia': 1,
    'cellulase': 1, #!!! note water content
    'CSL': 1,
    'caustic': 1, #!!! note water content    
    'FGD_lime': 1, #!!! need to be clear if this is CaO or Ca(OH)2
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
