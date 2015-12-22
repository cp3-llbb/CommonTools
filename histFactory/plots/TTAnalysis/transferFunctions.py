import inspect
import os
import sys

# Get directory where script is stored to handle the import correctly
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)

from plotTools import *

## Transfer Functions

bjet_binningX = range(0, 200, 5) + range(200, 400, 20) + [400, 450, 500, 550, 600, 700, 800, 2000]
bjet_binningY = [-500, -400] + range(-300, -200, 50) + range(-200, -50, 10) + range(-50, 0, 5) + range(0, 50, 5) + range(50, 200, 10) + range(200, 300, 50) + [300, 400, 500]

bjet_BA_binningX = range(0, 200, 5) + range(200, 360, 20) + [360, 400, 1000] 
bjet_BA_binningY = range(-500, -200, 100) + range(-200, -100, 20) + range(-100, 0, 10) + range(0, 100, 10) + range(100, 200, 20) + range(200, 500, 100) + [500]

bjet_EC_binningX = range(0, 200, 10) + range(200, 500, 20) + [500, 550, 600, 800, 2000]
bjet_EC_binningY = range(-500, -200, 100) + range(-200, -50, 20) + range(-50, 0, 10) + range(0, 50, 10) + range(50, 200, 20) + range(200, 500, 100) + [500]

bjet_nBinsX = str(len(bjet_binningX)-1)
bjet_binningX = "{" + str(bjet_binningX).strip("[").strip("]") + "}"
bjet_nBinsY = str(len(bjet_binningY)-1)
bjet_binningY = "{" + str(bjet_binningY).strip("[").strip("]") + "}"

bjet_BA_nBinsX = str(len(bjet_BA_binningX)-1)
bjet_BA_binningX = "{" + str(bjet_BA_binningX).strip("[").strip("]") + "}"
bjet_BA_nBinsY = str(len(bjet_BA_binningY)-1)
bjet_BA_binningY = "{" + str(bjet_BA_binningY).strip("[").strip("]") + "}"

bjet_EC_nBinsX = str(len(bjet_EC_binningX)-1)
bjet_EC_binningX = "{" + str(bjet_EC_binningX).strip("[").strip("]") + "}"
bjet_EC_nBinsY = str(len(bjet_EC_binningY)-1)
bjet_EC_binningY = "{" + str(bjet_EC_binningY).strip("[").strip("]") + "}"

matchedBTFs = [
        # B-jet transfer functions using matched b-quarks over whole eta range
        {
            'name': 'TF_b_E_CAT_#CAT_TITLE#',
            'variable': 'pruned_gen_particle_p4[ tt_gen_b ].E() ::: tt_selJets[ tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_b[#MIN_LEP_IDISO#] ] ].p4.E() - pruned_gen_particle_p4[ tt_gen_b ].E()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#',
                'tt_gen_b >= 0', 'tt_gen_matched_b[#MIN_LEP_IDISO#] >= 0', '( tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first == tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_b[#MIN_LEP_IDISO#] ] || tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second == tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_b[#MIN_LEP_IDISO#] ])',
                'tt_gen_b_deltaR[#MIN_LEP_IDISO#][ tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_b[#MIN_LEP_IDISO#] ] ] < 0.3'
                ),
            'binning': '(' + bjet_nBinsX + ', ' + bjet_binningX + ', ' + bjet_nBinsY + ', ' + bjet_binningY + ')',
        },
        {
            'name': 'TF_bbar_E_CAT_#CAT_TITLE#',
            'variable': 'pruned_gen_particle_p4[ tt_gen_bbar ].E() ::: tt_selJets[ tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_bbar[#MIN_LEP_IDISO#] ] ].p4.E() - pruned_gen_particle_p4[ tt_gen_bbar ].E()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#',
                'tt_gen_bbar >= 0', 'tt_gen_matched_bbar[#MIN_LEP_IDISO#] >= 0', '( tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first == tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_bbar[#MIN_LEP_IDISO#] ] || tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second == tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_bbar[#MIN_LEP_IDISO#] ])',
                'tt_gen_bbar_deltaR[#MIN_LEP_IDISO#][ tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_bbar[#MIN_LEP_IDISO#] ] ] < 0.3'
                ),
            'binning': '(' + bjet_nBinsX + ', ' + bjet_binningX + ', ' + bjet_nBinsY + ', ' + bjet_binningY + ')',
        },

        # B-jet transfer functions using matched b-quarks in the barrel (|eta|<=1.3)
        {
            'name': 'TF_BA_b_E_CAT_#CAT_TITLE#',
            'variable': 'pruned_gen_particle_p4[ tt_gen_b ].E() ::: tt_selJets[ tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_b[#MIN_LEP_IDISO#] ] ].p4.E() - pruned_gen_particle_p4[ tt_gen_b ].E()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#',
                'abs(tt_selJets[ tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_b[#MIN_LEP_IDISO#] ] ].p4.Eta())<=1.3',
                'tt_gen_b >= 0', 'tt_gen_matched_b[#MIN_LEP_IDISO#] >= 0', '( tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first == tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_b[#MIN_LEP_IDISO#] ] || tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second == tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_b[#MIN_LEP_IDISO#] ])',
                'tt_gen_b_deltaR[#MIN_LEP_IDISO#][ tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_b[#MIN_LEP_IDISO#] ] ] < 0.3'
                ),
            'binning': '(' + bjet_BA_nBinsX + ', ' + bjet_BA_binningX + ', ' + bjet_BA_nBinsY + ', ' + bjet_BA_binningY + ')',
        },
        {
            'name': 'TF_BA_bbar_E_CAT_#CAT_TITLE#',
            'variable': 'pruned_gen_particle_p4[ tt_gen_bbar ].E() ::: tt_selJets[ tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_bbar[#MIN_LEP_IDISO#] ] ].p4.E() - pruned_gen_particle_p4[ tt_gen_bbar ].E()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#',
                'abs(tt_selJets[ tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_bbar[#MIN_LEP_IDISO#] ] ].p4.Eta())<=1.3',
                'tt_gen_bbar >= 0', 'tt_gen_matched_bbar[#MIN_LEP_IDISO#] >= 0', '( tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first == tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_bbar[#MIN_LEP_IDISO#] ] || tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second == tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_bbar[#MIN_LEP_IDISO#] ])',
                'tt_gen_bbar_deltaR[#MIN_LEP_IDISO#][ tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_bbar[#MIN_LEP_IDISO#] ] ] < 0.3'
                ),
            'binning': '(' + bjet_BA_nBinsX + ', ' + bjet_BA_binningX + ', ' + bjet_BA_nBinsY + ', ' + bjet_BA_binningY + ')',
        },

        # B-jet transfer functions using matched b-quarks in the endcaps (|eta|>1.3)
        {
            'name': 'TF_EC_b_E_CAT_#CAT_TITLE#',
            'variable': 'pruned_gen_particle_p4[ tt_gen_b ].E() ::: tt_selJets[ tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_b[#MIN_LEP_IDISO#] ] ].p4.E() - pruned_gen_particle_p4[ tt_gen_b ].E()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#',
                'abs(tt_selJets[ tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_b[#MIN_LEP_IDISO#] ] ].p4.Eta())>1.3',
                'tt_gen_b >= 0', 'tt_gen_matched_b[#MIN_LEP_IDISO#] >= 0', '( tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first == tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_b[#MIN_LEP_IDISO#] ] || tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second == tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_b[#MIN_LEP_IDISO#] ])',
                'tt_gen_b_deltaR[#MIN_LEP_IDISO#][ tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_b[#MIN_LEP_IDISO#] ] ] < 0.3'
                ),
            'binning': '(' + bjet_EC_nBinsX + ', ' + bjet_EC_binningX + ', ' + bjet_EC_nBinsY + ', ' + bjet_EC_binningY + ')',
        },
        {
            'name': 'TF_EC_bbar_E_CAT_#CAT_TITLE#',
            'variable': 'pruned_gen_particle_p4[ tt_gen_bbar ].E() ::: tt_selJets[ tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_bbar[#MIN_LEP_IDISO#] ] ].p4.E() - pruned_gen_particle_p4[ tt_gen_bbar ].E()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#',
                'abs(tt_selJets[ tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_bbar[#MIN_LEP_IDISO#] ] ].p4.Eta())>1.3',
                'tt_gen_bbar >= 0', 'tt_gen_matched_bbar[#MIN_LEP_IDISO#] >= 0', '( tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first == tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_bbar[#MIN_LEP_IDISO#] ] || tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second == tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_bbar[#MIN_LEP_IDISO#] ])',
                'tt_gen_bbar_deltaR[#MIN_LEP_IDISO#][ tt_selJets_selID_DRCut[#MIN_LEP_IDISO#][ tt_gen_matched_bbar[#MIN_LEP_IDISO#] ] ] < 0.3'
                ),
            'binning': '(' + bjet_EC_nBinsX + ', ' + bjet_EC_binningX + ', ' + bjet_EC_nBinsY + ', ' + bjet_EC_binningY + ')',
        },

    ]


