import inspect
import os
import sys

# Get directory where script is stored to handle the import correctly
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)

from plotTools import *

## Transfer Functions

bjet_binningX = range(30, 100, 5) + range(100, 200, 10) + range(200, 500, 25) + range(500, 700, 50) + range(700, 1500, 100) + [1500]
bjet_binningY = range(-200, -100, 50) + range(-100, -50, 10) + range(-50, 0, 5) + range(0, 50, 5) + range(50, 100, 10) + range(100, 200, 50) + [200]

bjet_nBinsX = str(len(bjet_binningX)-1)
bjet_binningX = "{" + str(bjet_binningX).strip("[").strip("]") + "}"
bjet_nBinsY = str(len(bjet_binningY)-1)
bjet_binningY = "{" + str(bjet_binningY).strip("[").strip("]") + "}"
                
TFs = [
        # B-jet transfer functions
        {
            'name': 'TF_bjet1_E_CAT_#CAT_TITLE#',
            'variable': 'jet_gen_p4[ tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first ].idx ].E() : tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first ].p4.E() - jet_gen_p4[ tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first ].idx ].E()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#',
                'jet_has_matched_gen_particle[ tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first ].idx ]'
                ),
            'binning': '(' + bjet_nBinsX + ', ' + bjet_binningX + ', ' + bjet_nBinsY + ', ' + bjet_binningY + ')',
        },
        {
            'name': 'TF_bjet2_E_CAT_#CAT_TITLE#',
            'variable': 'jet_gen_p4[ tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second ].idx ].E() : tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second ].p4.E() - jet_gen_p4[ tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second ].idx ].E()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#',
                'jet_has_matched_gen_particle[ tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second ].idx ]'
                ),
            'binning': '(' + bjet_nBinsX + ', ' + bjet_binningX + ', ' + bjet_nBinsY + ', ' + bjet_binningY + ')',
        }
    ]


