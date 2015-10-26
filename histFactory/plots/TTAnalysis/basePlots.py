import inspect
import os
import sys

# Get directory where script is stored to handle the import correctly
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)

from plotTools import *

# Define skeleton config for plots, with stringcards which will be replaced for each category

ll = [
        # Lepton 1
        { 
            'name': 'lep1_pt_CAT_#CAT_TITLE#',
            'variable': 'tt_leptons[ tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].lidxs.first ].p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 20, 320)
        },
        { 
            'name': 'lep1_eta_CAT_#CAT_TITLE#',
            'variable': 'tt_leptons[ tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].lidxs.first ].p4.Eta()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, -2.5, 2.5)
        },
        { 
            'name': 'lep1_phi_CAT_#CAT_TITLE#',
            'variable': 'tt_leptons[ tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].lidxs.first ].p4.Phi()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, -3.2, 3.2)
        },
        { 
            'name': 'lep1_iso_CAT_#CAT_TITLE#',
            'variable': 'tt_leptons[ tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].lidxs.first ].isoValue',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 0.2)
        },
        
        # Lepton 2
        { 
            'name': 'lep2_pt_CAT_#CAT_TITLE#',
            'variable': 'tt_leptons[ tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].lidxs.second ].p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 20, 320)
        },
        { 
            'name': 'lep2_eta_CAT_#CAT_TITLE#',
            'variable': 'tt_leptons[ tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].lidxs.second ].p4.Eta()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, -2.5, 2.5)
        },
        { 
            'name': 'lep2_phi_CAT_#CAT_TITLE#',
            'variable': 'tt_leptons[ tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].lidxs.second ].p4.Phi()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, -3.2, 3.2)
        },
        { 
            'name': 'lep2_iso_CAT_#CAT_TITLE#',
            'variable': 'tt_leptons[ tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].lidxs.second ].isoValue',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 0.2)
        },
        
        # DiLepton
        { 
            'name': 'll_M_CAT_#CAT_TITLE#',
            'variable': 'tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].p4.M()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (100, 0, 800)
        },
        { 
            'name': 'll_Pt_CAT_#CAT_TITLE#',
            'variable': 'tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 300)
        },
        { 
            'name': 'll_Eta_CAT_#CAT_TITLE#',
            'variable': 'tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].p4.Eta()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, -5, 5)
        },
        { 
            'name': 'll_Phi_CAT_#CAT_TITLE#',
            'variable': 'tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].p4.Phi()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, -3.2, 3.2)
        },
        { 
            'name': 'll_DR_CAT_#CAT_TITLE#',
            'variable': 'tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].DR',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 6)
        },
        #{ 
        #    'name': 'DEtall_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].DEta',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 5)
        #},
        { 
            'name': 'll_DPhi_CAT_#CAT_TITLE#',
            'variable': 'abs(tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].DPhi)',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 3.2)
        },
        
        # number of jets: also valid for categories with < 2 jets => put in here
        {
            'name': 'nJets_CAT_#CAT_TITLE#',
            'variable': 'Length$(tt_selJets_selID_DRCut[#MIN_LEP_IDISO#])',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (10, 0, 10)
        },
       
        # MissingET: same thing
        {
            'name': 'PFMET_MET_CAT_#CAT_TITLE#',
            'variable': 'met_p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 250)
        },
        #{
        #    'name': 'noHFMET_MET_CAT_#CAT_TITLE#',
        #    'variable': 'nohf_met_p4.Pt()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 250)
        #},

    ]

# Jet-related plots (also dependent on lepton infos because of the minDRjl cut)
lljj = [
        # Jet 1
        { 
            'name': 'jet1_pt_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].jidxs.first ].p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 30, 380)
        },
        { 
            'name': 'jet1_eta_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].jidxs.first ].p4.Eta()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, -2.5, 2.5)
        },
        { 
            'name': 'jet1_phi_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].jidxs.first ].p4.Phi()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, -3.2, 3.2)
        },
        #{ 
        #    'name': 'jet1_minDRjl_CAT_#CAT_TITLE#',
        #    'variable': 'tt_selJets[ tt_diJets[ diLepDiJets_DRCut[#LEPLEP_IDISO#][0].diJetIdx ].jidxs.first ].minDRjl_lepIDIso[#MIN_LEP_IDISO#]',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 6)
        #},
        { 
            'name': 'jet1_CSVv2_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].jidxs.first ].CSVv2',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 1)
        },
        
        # Jet 2
        { 
            'name': 'jet2_pt_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].jidxs.second ].p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 30, 380)
        },
        { 
            'name': 'jet2_eta_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].jidxs.second ].p4.Eta()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, -2.5, 2.5)
        },
        { 
            'name': 'jet2_phi_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].jidxs.second ].p4.Phi()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, -3.2, 3.2)
        },
        #{ 
        #    'name': 'jet2_minDRjl_CAT_#CAT_TITLE#',
        #    'variable': 'tt_selJets[ tt_diJets[ diLepDiJets_DRCut[#LEPLEP_IDISO#][0].diJetIdx ].jidxs.second ].minDRjl_lepIDIso[#MIN_LEP_IDISO#]',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 6)
        #},
        { 
            'name': 'jet2_CSVv2_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].jidxs.second ].CSVv2',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 1)
        },

        # DiJet
        { 
            'name': 'jj_M_CAT_#CAT_TITLE#',
            'variable': 'tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].p4.M()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (100, 0, 800)
        },
        { 
            'name': 'jj_Pt_CAT_#CAT_TITLE#',
            'variable': 'tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 500)
        },
        { 
            'name': 'jj_Eta_CAT_#CAT_TITLE#',
            'variable': 'tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].p4.Eta()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, -5, 5)
        },
        { 
            'name': 'jj_Phi_CAT_#CAT_TITLE#',
            'variable': 'tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].p4.Phi()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, -3.2, 3.2)
        },
        { 
            'name': 'jj_DR_CAT_#CAT_TITLE#',
            'variable': 'tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].DR',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 6)
        },
        { 
            'name': 'jj_DPhi_CAT_#CAT_TITLE#',
            'variable': 'abs(tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].DPhi)',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 3.2)
        },
        
        # DiLepDiJet
        { 
            'name': 'lljj_M_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].p4.M()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 800)
        },
        { 
            'name': 'lljj_Pt_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 500)
        },
        { 
            'name': 'lljj_Eta_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].p4.Eta()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, -5, 5)
        },
        { 
            'name': 'lljj_Phi_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].p4.Phi()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, -3.2, 3.2)
        },
        { 
            'name': 'lljj_DR_ll_jj_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].DR_ll_jj',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 6)
        },
        { 
            'name': 'lljj_DPhi_ll_jj_CAT_#CAT_TITLE#',
            'variable': 'abs(tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].DPhi_ll_jj)',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 3.2)
        },
        { 
            'name': 'lljj_minDRjl_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].minDRjl',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 6)
        },
        { 
            'name': 'lljj_maxDRjl_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].maxDRjl',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 6)
        },
        { 
            'name': 'lljj_minDPhijl_CAT_#CAT_TITLE#',
            'variable': 'abs(tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].minDPhijl)',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 3.2)
        },
        { 
            'name': 'lljj_maxDPhijl_CAT_#CAT_TITLE#',
            'variable': 'abs(tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].maxDPhijl)',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 3.2)
        },
    ]

# BJet-related plots (also dependent on lepton infos because of the minDRjl cut)
# For now, take CSVv2-chosen di-bjets
# Only require two jets but iterate over one b-tag working point
lljj_b = [
        # number of b-jets
        { 
            'name': 'nBJets_#BWP#_CAT_#CAT_TITLE#',
            'variable': 'Length$(tt_selBJets_DRCut_BWP_CSVv2Ordered[#MIN_LEP_IDISO_BWP#])',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (6, 0, 6)
        },
    ]

# BJet-related plots (also dependent on lepton infos because of the minDRjl cut)
# For now, take CSVv2-chosen di-bjets
# Require two jets and one b-jet; iterate over one b-tag working point
llbj = [ ]

# (ll)bb(Met)-related plots
# For now, take CSVv2-chosen di-bjets
# Require two jets and loop over two b-tag working points
llbb = [
        # BJet 1
        { 
            'name': 'bjet1_pt_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first ].p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 30, 380)
        },
        { 
            'name': 'bjet1_eta_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first ].p4.Eta()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, -2.5, 2.5)
        },
        { 
            'name': 'bjet1_phi_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first ].p4.Phi()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, -3.2, 3.2)
        },
        #{ 
        #    'name': 'bjet1_minDRjl_CAT_#CAT_TITLE#',
        #    'variable': 'tt_selJets[ tt_diJets[ [ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first ].jidxs.first ].minDRjl_lepIDIso[#MIN_LEP_IDISO#]',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 6)
        #},
        { 
            'name': 'bjet1_CSVv2_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first ].CSVv2',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 1)
        },
        
        # BJet 2
        { 
            'name': 'bjet2_pt_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second ].p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 30, 380)
        },
        { 
            'name': 'bjet2_eta_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second ].p4.Eta()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, -2.5, 2.5)
        },
        { 
            'name': 'bjet2_phi_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second ].p4.Phi()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, -3.2, 3.2)
        },
        #{ 
        #    'name': 'bjet2_minDRjl_CAT_#CAT_TITLE#',
        #    'variable': 'tt_selJets[ tt_diJets[ [ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first ].jidxs.second ].minDRjl_lepIDIso[#MIN_LEP_IDISO#]',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 6)
        #},
        { 
            'name': 'bjet2_CSVv2_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second ].CSVv2',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 1)
        },
        
        # DiBJet
        { 
            'name': 'bb_M_CAT_#CAT_TITLE#',
            'variable': 'tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].p4.M()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 800)
        },
        { 
            'name': 'bb_Pt_CAT_#CAT_TITLE#',
            'variable': 'tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 500)
        },
        { 
            'name': 'bb_Eta_CAT_#CAT_TITLE#',
            'variable': 'tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].p4.Eta()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, -5, 5)
        },
        { 
            'name': 'bb_Phi_CAT_#CAT_TITLE#',
            'variable': 'tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].p4.Phi()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, -3.2, 3.2)
        },
        { 
            'name': 'bb_DR_CAT_#CAT_TITLE#',
            'variable': 'tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].DR',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 6)
        },
        { 
            'name': 'bb_DPhi_CAT_#CAT_TITLE#',
            'variable': 'abs(tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].DPhi)',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 3.2)
        },

        # DiLepDiBJet
        { 
            'name': 'llbb_M_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].p4.M()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 800)
        },
        { 
            'name': 'llbb_Pt_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 500)
        },
        { 
            'name': 'llbb_Eta_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].p4.Eta()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, -5, 5)
        },
        { 
            'name': 'llbb_Phi_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].p4.Phi()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, -3.2, 3.2)
        },
        { 
            'name': 'llbb_DR_ll_bb_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].DR_ll_jj',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 6)
        },
        { 
            'name': 'llbb_DPhi_ll_bb_CAT_#CAT_TITLE#',
            'variable': 'abs(tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].DPhi_ll_jj)',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 3.2)
        },
        { 
            'name': 'llbb_minDRjl_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].minDRjl',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 6)
        },
        { 
            'name': 'llbb_maxDRjl_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].maxDRjl',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 6)
        },
        { 
            'name': 'llbb_minDPhijl_CAT_#CAT_TITLE#',
            'variable': 'abs(tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].minDPhijl)',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 3.2)
        },
        { 
            'name': 'llbb_maxDPhijl_CAT_#CAT_TITLE#',
            'variable': 'abs(tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].maxDPhijl)',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 3.2)
        },
    ]
