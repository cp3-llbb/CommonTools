
# binnings

pt_binning  = "(30, 0, 300)"
eta_binning = "(30, 0, 6)"
phi_binning = "(30, -TMath::Pi(), TMath::Pi())"
lepiso_binning = "(30, 0, 0.3)"
mj_binning = "(30, 0, 30)"
csv_binning = "(10,0,1)"
DR_binning = "(30, 0, 6)"

# Leptons variables

l1 = "dilep_ptOrdered[0]"
l2 = "dilep_ptOrdered[1]"

l_var = ["p4.Pt()", "p4.Eta()", "p4.Phi()", "isoValue"]

l_binning = [pt_binning, eta_binning, phi_binning, lepiso_binning]

# Jets variables

j1Pt = "dijet_ptOrdered[0]"
j2pt = "dijet_ptOrdered[1]"

j1csv = "dijet_CSVv2Ordered[0]"
j2csv = "dijet_CSVv2Ordered[1]"

jets_var = ["p4.Pt()", "p4.Eta()", "p4.Phi()", "p4.M()", "CSVv2", "minDRjl" ]
jets_binning = [pt_binning, eta_binning, phi_binning, mj_binning, csv_binning, DR_binning]

# Dilep variables

dilep = "diLeptons[0]"

dilep_var = ["p4.Pt()", "p4.Eta()", "p4.Phi()", "p4.M", "DR", "DEta", "DPhi"]



# Cuts

twoMuTwojets ="(mumu_DileptonIsIDMM_cut * mumu_Mll_cut) * event_weight'"
twoMuTwojetsMM = "(mumu_DileptonIsIDMM_cut * mumu_Mll_cut * mumu_DiJetBWP_MM_cut) * event_weight'"

twoMuTwojets ="(elel_DileptonIsIDMM_cut * elel_Mll_cut) * event_weight'"
twoMuTwojetsMM = "(elel_DileptonIsIDMM_cut * elel_Mll_cut * elel_DiJetBWP_MM_cut) * event_weight'"


#print l_var[0]


# Writing the JSON

f = open('plots_twoMuTwojets.json', 'w')
for i in range(0, len(l_var)) :

  f.write( "'plots = [{'\n")
  f.write( "        'name': '"+l1+"_"+l_var[i]+"' ,\n")
  f.write( "        'variable': '"+l1+"."+l_var[i]+"',\n")
  f.write( "        'plot_cut': '"+twoMuTwojets+"',\n")
  f.write( "        'binning': '"+l_binning[i]+"'\n")
  f.write( "        }]\n")

