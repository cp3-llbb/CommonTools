#### This file is passed to histFactory
#### It generates all the plot configs based on skeletons defined in basePlots
####  and on info defined in plotTools.

import inspect
import os
import sys

#### Get directory where script is stored to handle the import correctly
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)

from TTAnalysis import pathCMS

#### Get dictionary definitions ####
from plotTools import *

#### Get plot skeletons from other file ####
import basePlots
import transferFunctions 

#### Define the sub-categories and the corresponding plot groups ####

categoryPlots = {
        
        ## ask for 2 leptons; vary over lepton ID & iso for two leptons
        #"llCategs": { 
        #    "plots": basePlots.ll,
        #    },
        
        # ask for 2 leptons & 2 jets; vary over lepton ID & iso for two leptons(take loosest ones for jet minDRjl cut)
        "lljjCategs": { 
            "plots": basePlots.ll + basePlots.lljj,
            },
        
        # ask for 2 leptons & 2 jets; vary over lepton ID & iso for two leptons (take loosest ones for jet minDRjl cut), and one b-tag working point
        "lljj_b_Categs": { 
            "plots": basePlots.lljj_b,
            },
        
        # ask for 2 leptons & 2 jets & 1 b-jet; vary over lepton ID & iso for two leptons (take loosest ones for jet minDRjl cut), and one b-tag working point
        "llbjCategs": { 
            "plots": basePlots.llbj,
            },
        
        # ask for 2 leptons & 2 b-jets; vary over lepton ID & iso for two leptons (take loosest ones for jet minDRjl cut), and two b-tag working point
        "llbbCategs": { 
            "plots": basePlots.ll + basePlots.lljj + basePlots.llbb,
            #"plots": transferFunctions.matchedBTFs,
            },
    
    }

# Initialize maps needed later
for categ in categoryPlots.values():
    categ["strings"] = []
    categ["weights"] = []


flavourCategPlots = { flav: copy.deepcopy(categoryPlots) for flav in myFlavours }

for flav in flavourCategPlots.items():
    generateCategoryStrings(flav[1], flav[0])

#### Generate all the plots ####

plots = []

# Iterate over ll flavours
for flav in flavourCategPlots.values():

    # Iterate over category groups
    for categ in flav.values():

        # Iterate over each sub-category
        for subCateg_index, subCateg in enumerate(categ["strings"]):

            # Iterate over every plot skeleton defined for the current category group
            for plot in categ["plots"]:
                m_plot = copy.deepcopy(plot)
                if not 'scale-factors' in m_plot:
                    m_plot['scale-factors'] = True

                # Iterate over the string keys defined in the sub-category
                for key in subCateg.items():

                    # Update name, variable, and plot_cut field
                    for field in m_plot.keys():
                        if isinstance(m_plot[field], str):
                            m_plot[field] = m_plot[field].replace(key[0], str(key[1]))

                # Replace binning tuples by strings
                m_plot["binning"] = str(m_plot["binning"])

                # Plot weights
                m_plot["weight"] = "event_pu_weight * event_weight"
                if len(categ["weights"][subCateg_index]) > 0 and m_plot['scale-factors']:
                    m_plot["weight"] += " * " + "({})".format(") * (".join(categ["weights"][subCateg_index]))

                plots.append(m_plot)

                print "Plot: {}\nVariable: {}\nCut: {}\nWeight: {}\nBinning: {}\n".format(m_plot["name"], m_plot["variable"], m_plot["plot_cut"], m_plot["weight"], m_plot["binning"])

print "Generated {} plots.\n".format(len(plots))
