
# binnings

pt_binning  = "(30, 0, 300)"
eta_binning = "(30, 0, 6)"
phi_binning = "(30, -3.1416, 3.1416"
lepiso_binning = "(30, 0, 0.3)"
mj_binning = "(30, 0, 30)"
csv_binning = "(10,0,1)"
DR_binning = "(30, 0, 6)"
MZ_binning = "(300,0,300)"

# Leptons variables

l1 = "za_dilep_ptOrdered[0]"
l2 = "za_dilep_ptOrdered[1]"

l1Name = "za_dilep_ptOrdered0"
l2Name = "za_dilep_ptOrdered1"

l_var = ["p4.Pt()", "p4.Eta()", "p4.Phi()", "isoValue"]
l_varName = ["Pt", "Eta", "Phi", "isoValue"]

l_binning = [pt_binning, eta_binning, phi_binning, lepiso_binning]

# Jets variables

j1Pt = "za_dijet_ptOrdered[0]"
j2pt = "za_dijet_ptOrdered[1]"

j1csv = "za_dijet_CSVv2Ordered[0]"
j2csv = "za_dijet_CSVv2Ordered[1]"

jets_var = ["p4.Pt()", "p4.Eta()", "p4.Phi()", "p4.M()", "CSVv2", "minDRjl" ]
jets_binning = [pt_binning, eta_binning, phi_binning, mj_binning, csv_binning, DR_binning]

# Dilep variables

dilep = "za_diLeptons[0]"
dilep_name = "za_diLeptons0"

dilep_var = ["p4.Pt()", "p4.Eta()", "p4.Phi()", "p4.M()", "DR", "DEta", "DPhi"]
dilep_varName = ["Pt", "Eta", "Phi", "M", "DR", "DEta", "DPhi"]

dilep_binning = [pt_binning, eta_binning, phi_binning, MZ_binning, DR_binning, DR_binning, DR_binning]
# Cuts

twoMuTwojets ="(mumu_DileptonIsIDMM_cut * mumu_Mll_cut) * event_weight"
twoMuTwojetsMM = "(mumu_DileptonIsIDMM_cut * mumu_Mll_cut * mumu_DiJetBWP_MM_cut) * event_weight"

twoElTwojets ="(elel_DileptonIsIDMM_cut * elel_Mll_cut) * event_weight"
twoElTwojetsMM = "(elel_DileptonIsIDMM_cut * elel_Mll_cut * elel_DiJetBWP_MM_cut) * event_weight"


#print l_var[0]


# Writing the JSON

f = open('plots_twoMuTwojets.json', 'w')
f.write( "plots = [\n")
for i in range(0, len(l_var)) :
  f.write( "        {\n")
  f.write( "        'name': '"+l1Name+"_"+l_varName[i]+"',\n")
  f.write( "        'variable': '"+l1+"."+l_var[i]+"',\n")
  f.write( "        'plot_cut': '"+twoMuTwojets+"',\n")
  f.write( "        'binning': '"+l_binning[i]+"'\n")
  f.write( "        },\n")

for i in range(0, len(dilep_var)) :
  f.write( "        {\n")
  f.write( "        'name': '"+dilep_name+"_"+dilep_varName[i]+"',\n")
  f.write( "        'variable': '"+dilep+"."+dilep_var[i]+"',\n")
  f.write( "        'plot_cut': '"+twoMuTwojetsMM+"',\n")
  f.write( "        'binning': '"+dilep_binning[i]+"'\n")
  if i != len(dilep_var)-1 :
    f.write( "        },\n")

f.write( "        }]\n")
