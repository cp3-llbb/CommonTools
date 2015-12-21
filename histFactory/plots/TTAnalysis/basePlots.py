import inspect
import os
import sys

# Get directory where script is stored to handle the import correctly
scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(scriptDir)

from plotTools import *

# Define skeleton config for plots, with stringcards which will be replaced for each category

ll = [
        ## Event/vertex infos
        #{
        #    'name': 'nPV_CAT_#CAT_TITLE#',
        #    'variable': 'Length$(vertex_ndof)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 50)
        #},

        ## Gen plots
        {
            'name': 'gen_TT_M_BeforeFSR_CAT_#CAT_TITLE#',
            'variable': 'tt_gen_ttbar_beforeFSR_p4.M()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_gen_ttbar_decay_type > 0'),
            'binning': (100, 300, 3000)
        },
        {
            'name': 'gen_TT_Pt_BeforeFSR_CAT_#CAT_TITLE#',
            'variable': 'tt_gen_ttbar_beforeFSR_p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_gen_ttbar_decay_type > 0'),
            'binning': (100, 300, 3000)
        },
        {
            'name': 'gen_TT_Eta_BeforeFSR_CAT_#CAT_TITLE#',
            'variable': 'tt_gen_ttbar_beforeFSR_p4.Eta()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_gen_ttbar_decay_type > 0'),
            'binning': (50, -6, 6)
        },
        {
            'name': 'gen_TT_M_CAT_#CAT_TITLE#',
            'variable': 'tt_gen_ttbar_p4.M()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_gen_ttbar_decay_type > 0'),
            'binning': (100, 300, 3000)
        },
        {
            'name': 'gen_TT_Pt_CAT_#CAT_TITLE#',
            'variable': 'tt_gen_ttbar_p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_gen_ttbar_decay_type > 0'),
            'binning': (100, 300, 3000)
        },
        {
            'name': 'gen_TT_Eta_CAT_#CAT_TITLE#',
            'variable': 'tt_gen_ttbar_p4.Eta()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_gen_ttbar_decay_type > 0'),
            'binning': (50, -6, 6)
        },

        ## nLeptons
        { 
            'name': 'nElectrons_CAT_#CAT_TITLE#',
            'variable': 'Length$(tt_electrons_IDIso[#EL_IDISO#])',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (5, 0, 5),
            'scale-factors': False
        },
        { 
            'name': 'nMuons_CAT_#CAT_TITLE#',
            'variable': 'Length$(tt_muons_IDIso[#MU_IDISO#])',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 0.2)
            'scale-factors': False
        },

        ## Lepton 1
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
        #{ 
        #    'name': 'lep1_phi_CAT_#CAT_TITLE#',
        #    'variable': 'tt_leptons[ tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].lidxs.first ].p4.Phi()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, -3.14159, 3.14159)
        #},
        { 
            'name': 'lep1_iso_CAT_#CAT_TITLE#',
            'variable': 'tt_leptons[ tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].lidxs.first ].isoValue',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 0.2)
        },
        { 
            'name': 'lep1_SF_CAT_#CAT_TITLE#',
            'variable': '#LEP1_SF#',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0.7, 1.3),
            'scale-factors': False
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
        #{ 
        #    #'name': 'lep2_phi_CAT_#CAT_TITLE#',
        #    #'variable': 'tt_leptons[ tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].lidxs.second ].p4.Phi()',
        #    #'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    #'binning': (50, -3.14159, 3.14159)
        #},
        { 
            'name': 'lep2_iso_CAT_#CAT_TITLE#',
            'variable': 'tt_leptons[ tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].lidxs.second ].isoValue',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 0.2)
        },
        { 
            'name': 'lep2_SF_CAT_#CAT_TITLE#',
            'variable': '#LEP2_SF#',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0.7, 1.3),
            'scale-factors': False
        },
        
        # DiLepton
        { 
            'name': 'll_M_CAT_#CAT_TITLE#',
            'variable': 'tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].p4.M()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (100, 0, 800)
        },
        { 
            'name': 'll_M_Zpeak_CAT_#CAT_TITLE#',
            'variable': 'tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].p4.M()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 70, 110)
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
        #{ 
        #    'name': 'll_Phi_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].p4.Phi()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, -3.14159, 3.14159)
        #},
        { 
            'name': 'll_DR_CAT_#CAT_TITLE#',
            'variable': 'tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].DR',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 6)
        },
        #{ 
        #    'name': 'll_DEta_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].DEta',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 5)
        #},
        #{ 
        #    'name': 'll_DPhi_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLeptons[ tt_diLeptons_IDIso[#LEPLEP_IDISO#][0] ].DPhi)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        
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
        {
            'name': 'PFFMET_Phi_CAT_#CAT_TITLE#',
            'variable': 'met_p4.Phi()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, -3.14159, 3.14159)
        },
        #{
        #    'name': 'noHFMET_MET_CAT_#CAT_TITLE#',
        #    'variable': 'nohf_met_p4.Pt()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 250)
        #},
        #{
        #    'name': 'noHFMET_Phi_CAT_#CAT_TITLE#',
        #    'variable': 'nohf_met_p4.Phi()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, -3.14159, 3.14159)
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
        #{ 
        #    'name': 'jet1_phi_CAT_#CAT_TITLE#',
        #    'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].jidxs.first ].p4.Phi()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, -3.14159, 3.14159)
        #},
        { 
            'name': 'jet1_minDRjl_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].jidxs.first ].minDRjl_lepIDIso[#MIN_LEP_IDISO#]',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 6)
        },
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
        #{ 
        #    'name': 'jet2_phi_CAT_#CAT_TITLE#',
        #    'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].jidxs.second ].p4.Phi()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, -3.14159, 3.14159)
        #},
        { 
            'name': 'jet2_minDRjl_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].jidxs.second ].minDRjl_lepIDIso[#MIN_LEP_IDISO#]',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 6)
        },
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
        #{ 
        #    'name': 'jj_Phi_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].p4.Phi()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, -3.14159, 3.14159)
        #},
        { 
            'name': 'jj_DR_CAT_#CAT_TITLE#',
            'variable': 'tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].DR',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 6)
        },
        #{ 
        #    'name': 'jj_DEta_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].DEta',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 10)
        #},
        #{ 
        #    'name': 'jj_DPhi_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diJets[ tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].diJetIdx ].DPhi)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        
        # DiLepDiJet
        { 
            'name': 'lljj_M_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].p4.M()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 100, 1500)
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
        #{ 
        #    'name': 'lljj_Phi_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].p4.Phi()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, -3.14159, 3.14159)
        #},
        { 
            'name': 'lljj_DR_ll_jj_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].DR_ll_jj',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 6)
        },
        #{ 
        #    'name': 'lljj_DEta_ll_jj_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].DEta_ll_jj',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 10)
        #},
        #{ 
        #    'name': 'lljj_DPhi_ll_jj_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].DPhi_ll_jj)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
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
        #{ 
        #    'name': 'lljj_minDEtajl_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].minDEtajl',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 5)
        #},
        #{ 
        #    'name': 'lljj_maxDEtajl_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].maxDEtajl',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 5)
        #},
        #{ 
        #    'name': 'lljj_minDPhijl_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].minDPhijl)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        #{ 
        #    'name': 'lljj_maxDPhijl_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJets[ tt_diLepDiJets_DRCut[#LEPLEP_IDISO#][0] ].maxDPhijl)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        
        # DiLepDiJetMET
        { 
            'name': 'lljjMet_Pt_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJetsMet[ tt_diLepDiJetsMet_DRCut[#LEPLEP_IDISO#][0] ].p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 800)
        },
        #{ 
        #    'name': 'lljjMet_Phi_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diLepDiJetsMet[ tt_diLepDiJetsMet_DRCut[#LEPLEP_IDISO#][0] ].p4.Phi()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, -3.14159, 3.14159)
        #},
        { 
            'name': 'lljjMet_Mt_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJetsMet[ tt_diLepDiJetsMet_DRCut[#LEPLEP_IDISO#][0] ].p4.Mt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 100, 1500)
        },
        #{ 
        #    'name': 'lljjMet_DPhi_ll_Met_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJetsMet[ tt_diLepDiJetsMet_DRCut[#LEPLEP_IDISO#][0] ].DPhi_ll_Met)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        #{ 
        #    'name': 'lljjMet_DPhi_jj_Met_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJetsMet[ tt_diLepDiJetsMet_DRCut[#LEPLEP_IDISO#][0] ].DPhi_jj_Met)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        #{ 
        #    'name': 'lljjMet_DPhi_lljj_Met_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJetsMet[ tt_diLepDiJetsMet_DRCut[#LEPLEP_IDISO#][0] ].DPhi_lljj_Met)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        #{ 
        #    'name': 'lljjMet_minDPhi_l_Met_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJetsMet[ tt_diLepDiJetsMet_DRCut[#LEPLEP_IDISO#][0] ].minDPhi_l_Met)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        #{ 
        #    'name': 'lljjMet_maxDPhi_l_Met_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJetsMet[ tt_diLepDiJetsMet_DRCut[#LEPLEP_IDISO#][0] ].maxDPhi_l_Met)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        #{ 
        #    'name': 'lljjMet_minDPhi_j_Met_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJetsMet[ tt_diLepDiJetsMet_DRCut[#LEPLEP_IDISO#][0] ].minDPhi_j_Met)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        #{ 
        #    'name': 'lljjMet_maxDPhi_j_Met_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJetsMet[ tt_diLepDiJetsMet_DRCut[#LEPLEP_IDISO#][0] ].maxDPhi_j_Met)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        
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
        #{ 
        #    'name': 'bjet1_phi_CAT_#CAT_TITLE#',
        #    'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first ].p4.Phi()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (25, -3.14159, 3.14159)
        #},
        { 
            'name': 'bjet1_minDRjl_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first ].minDRjl_lepIDIso[#MIN_LEP_IDISO#]',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 6)
        },
        { 
            'name': 'bjet1_CSVv2_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.first ].CSVv2',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 1)
        },
        { 
            'name': 'bjet1_SF_CAT_#CAT_TITLE#',
            'variable': '#BJET1_SF#',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0.7, 1.3),
            'scale-factors': False
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
        #{ 
        #    'name': 'bjet2_phi_CAT_#CAT_TITLE#',
        #    'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second ].p4.Phi()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (25, -3.14159, 3.14159)
        #},
        { 
            'name': 'bjet2_minDRjl_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second ].minDRjl_lepIDIso[#MIN_LEP_IDISO#]',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 6)
        },
        { 
            'name': 'bjet2_CSVv2_CAT_#CAT_TITLE#',
            'variable': 'tt_selJets[ tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].jidxs.second ].CSVv2',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 1)
        },
        { 
            'name': 'bjet2_SF_CAT_#CAT_TITLE#',
            'variable': '#BJET2_SF#',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0.7, 1.3),
            'scale-factors': False
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
        #{ 
        #    'name': 'bb_Phi_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].p4.Phi()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (25, -3.14159, 3.14159)
        #},
        { 
            'name': 'bb_DR_CAT_#CAT_TITLE#',
            'variable': 'tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].DR',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 6)
        },
        #{ 
        #    'name': 'bb_DEta_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].DEta',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (25, 0, 10)
        #},
        #{ 
        #    'name': 'bb_DPhi_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diJets[ tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].diJetIdx ].DPhi)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (25, 0, 3.14159)
        #},

        # DiLepDiBJet
        { 
            'name': 'llbb_M_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].p4.M()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 100, 1500)
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
        #{ 
        #    'name': 'llbb_Phi_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].p4.Phi()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (25, -3.14159, 3.14159)
        #},
        { 
            'name': 'llbb_DR_ll_bb_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].DR_ll_jj',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (25, 0, 6)
        },
        #{ 
        #    'name': 'llbb_DEta_ll_bb_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].DEta_ll_jj',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (25, 0, 10)
        #},
        #{ 
        #    'name': 'llbb_DPhi_ll_bb_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].DPhi_ll_jj)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (25, 0, 3.14159)
        #},
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
        #{ 
        #    'name': 'llbb_minDEtajl_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].minDEtajl',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (25, 0, 5)
        #},
        #{ 
        #    'name': 'llbb_maxDEtajl_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].maxDEtajl',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (25, 0, 5)
        #},
        #{ 
        #    'name': 'llbb_minDPhijl_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].minDPhijl)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (25, 0, 3.14159)
        #},
        #{ 
        #    'name': 'llbb_maxDPhijl_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJets[ tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].maxDPhijl)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (25, 0, 3.14159)
        #},
        
        # DiLepDiBJetMET
        { 
            'name': 'llbbMet_Pt_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJetsMet[ tt_diLepDiBJetsMet_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 0, 800)
        },
        #{ 
        #    'name': 'llbbMet_Phi_CAT_#CAT_TITLE#',
        #    'variable': 'tt_diLepDiJetsMet[ tt_diLepDiBJetsMet_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].p4.Phi()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, -3.14159, 3.14159)
        #},
        { 
            'name': 'llbbMet_Mt_CAT_#CAT_TITLE#',
            'variable': 'tt_diLepDiJetsMet[ tt_diLepDiBJetsMet_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].p4.Mt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
            'binning': (50, 100, 1500)
        },
        #{ 
        #    'name': 'llbbMet_DPhi_ll_Met_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJetsMet[ tt_diLepDiBJetsMet_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].DPhi_ll_Met)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        #{ 
        #    'name': 'llbbMet_DPhi_bb_Met_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJetsMet[ tt_diLepDiBJetsMet_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].DPhi_jj_Met)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        #{ 
        #    'name': 'llbbMet_DPhi_llbb_Met_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJetsMet[ tt_diLepDiBJetsMet_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].DPhi_lljj_Met)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        #{ 
        #    'name': 'llbbMet_minDPhi_l_Met_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJetsMet[ tt_diLepDiBJetsMet_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].minDPhi_l_Met)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        #{ 
        #    'name': 'llbbMet_maxDPhi_l_Met_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJetsMet[ tt_diLepDiBJetsMet_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].maxDPhi_l_Met)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        #{ 
        #    'name': 'llbbMet_minDPhi_j_Met_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJetsMet[ tt_diLepDiBJetsMet_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].minDPhi_j_Met)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        #{ 
        #    'name': 'llbbMet_maxDPhi_j_Met_CAT_#CAT_TITLE#',
        #    'variable': 'abs(tt_diLepDiJetsMet[ tt_diLepDiBJetsMet_DRCut_BWP_CSVv2Ordered[#LEPLEP_IDISO_BBWP#][0] ].maxDPhi_j_Met)',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#'),
        #    'binning': (50, 0, 3.14159)
        #},
        { 
            'name': 'llbbMet_TT_M_CAT_#CAT_TITLE#',
            'variable': 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0][0].p4.M()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0].size() > 0'),
            'binning': (50, 250, 3000)
        },
        { 
            'name': 'llbbMet_TT_Pt_CAT_#CAT_TITLE#',
            'variable': 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0][0].p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0].size() > 0'),
            'binning': (50, 0, 500)
        },
        { 
            'name': 'llbbMet_TT_Eta_CAT_#CAT_TITLE#',
            'variable': 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0][0].p4.Eta()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0].size() > 0'),
            'binning': (25, -5, 5)
        },
        ## MTT Resolution
        #{ 
        #    'name': 'llbbMet_TT_M_minus_Mgen_beforeFSR_CAT_#CAT_TITLE#',
        #    'variable': 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0][0].p4.M() - tt_gen_ttbar_beforeFSR_p4.M()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0].size() > 0', 'tt_gen_ttbar_decay_type > 0'),
        #    'binning': (100, -1000, 1000)
        #},
        #{ 
        #    'name': 'llbbMet_TT_M_resolution_beforeFSR_CAT_#CAT_TITLE#',
        #    'variable': '(tt_ttbar[#LEPLEP_IDISO_BBWP#][0][0].p4.M() - tt_gen_ttbar_beforeFSR_p4.M()) / tt_gen_ttbar_beforeFSR_p4.M() ' ,
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0].size() > 0', 'tt_gen_ttbar_decay_type > 0'),
        #    'binning': (200, -10, 10)
        #},
        #{ 
        #    'name': 'llbbMet_TT_M_minus_Mgen_CAT_#CAT_TITLE#',
        #    'variable': 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0][0].p4.M() - tt_gen_ttbar_p4.M()',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0].size() > 0', 'tt_gen_ttbar_decay_type > 0'),
        #    'binning': (100, -1000, 1000)
        #},
        { 
            'name': 'llbbMet_TT_M_resolution_CAT_#CAT_TITLE#',
            'variable': '(tt_ttbar[#LEPLEP_IDISO_BBWP#][0][0].p4.M() - tt_gen_ttbar_p4.M()) / tt_gen_ttbar_p4.M() ' ,
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0].size() > 0', 'tt_gen_ttbar_decay_type > 0'),
            'binning': (200, -10, 10)
        },
        # Top 1
        { 
            'name': 'llbbMet_T1_Pt_CAT_#CAT_TITLE#',
            'variable': 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0][0].top1_p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0].size() > 0'),
            'binning': (50, 0, 500)
        },
        { 
            'name': 'llbbMet_T1_Eta_CAT_#CAT_TITLE#',
            'variable': 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0][0].top1_p4.Eta()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0].size() > 0'),
            'binning': (25, -5, 5)
        },
        # Top 2
        { 
            'name': 'llbbMet_T2_Pt_CAT_#CAT_TITLE#',
            'variable': 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0][0].top2_p4.Pt()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0].size() > 0'),
            'binning': (50, 0, 500)
        },
        { 
            'name': 'llbbMet_T2_Eta_CAT_#CAT_TITLE#',
            'variable': 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0][0].top2_p4.Eta()',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0].size() > 0'),
            'binning': (25, -5, 5)
        },
        #{ 
        #    'name': 'llbbMet_DPhi_top1_top2_CAT_#CAT_TITLE#',
        #    'variable': 'abs( tt_ttbar[#LEPLEP_IDISO_BBWP#][0][0].DPhi_tt )',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0].size() > 0'),
        #    'binning': (50, 0, 3.14159)
        #},
        { 
            'name': 'llbbMet_DR_top1_top2_CAT_#CAT_TITLE#',
            'variable': 'abs( tt_ttbar[#LEPLEP_IDISO_BBWP#][0][0].DR_tt )',
            'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0].size() > 0'),
            'binning': (50, 0, 6)
        },
        #{ 
        #    'name': 'llbbMet_DEta_top1_top2_CAT_#CAT_TITLE#',
        #    'variable': 'abs( tt_ttbar[#LEPLEP_IDISO_BBWP#][0][0].DEta_tt )',
        #    'plot_cut': joinCuts('#LEPLEP_CAT_CUTS#', '#JET_CAT_CUTS#', 'tt_ttbar[#LEPLEP_IDISO_BBWP#][0].size() > 0'),
        #    'binning': (50, 0, 6)
        #},
    ]
