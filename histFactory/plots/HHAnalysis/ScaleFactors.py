from HHAnalysis import HH


noScaleFactors = False

def lepton_id_to_string(wp):
    if wp == HH.lepID.L:
        return 'loose'
    #elif wp == HH.lepID.M:
    #    return 'medium'
    elif wp == HH.lepID.T:
        return 'tight'

    raise Exception('Unknown lepton id working point')

def lepton_iso_to_string(wp):
    if wp == HH.lepIso.L:
        return 'loose'
    elif wp == HH.lepIso.T:
        return 'tight'

    raise Exception('Unknown lepton iso working point')

def btag_wp_to_string(wp):
    if wp == HH.btagWP.L:
        return 'loose'
    elif wp == HH.btagWP.M:
        return 'medium'
    elif wp == HH.btagWP.T:
        return 'tight'

    raise Exception('Unknown b-tagging working point')

def sysVar_to_idx(sysVar): # Scale factors are given as a vector with first element being nominal, second being down fluctuated, third being up fluctuated.
    if sysVar == "nominal" :
        return '0'
    elif sysVar == "down" :
        return '1'
    elif sysVar == "up" :
        return '2'

    raise Exception('Unknown systematic variation. Must be "nominal", "up" or "down"')

def get_muon_id_sf(id, muon_idx, sysVar = "nominal"):
    return 'muon_sf_id_%s[%s][%s]' % (lepton_id_to_string(id), muon_idx, sysVar_to_idx(sysVar))

def get_muon_iso_sf(iso, id, muon_idx, sysVar = "nominal"):
    return 'muon_sf_iso_%s_id_%s[%s][%s]' % (lepton_iso_to_string(iso),  lepton_id_to_string(id), muon_idx, sysVar_to_idx(sysVar))

def get_csvv2_sf(wp, jet_idx, sysVar = "nominal"):
    if wp ==  HH.btagWP.no :
        return "1."
    return 'jet_sf_csvv2_%s[%s][%s]' % (btag_wp_to_string(wp), jet_idx, sysVar_to_idx(sysVar))

# lepton scale factors

def get_lepton_SF(hh_lepton, id, iso, sysVar = "nominal"):
    lep_fwkIdx = hh_lepton+".idx"
    return '(({0}.isEl) ? 1. : {1} * {2})'.format(hh_lepton, get_muon_id_sf(id, lep_fwkIdx, sysVar), get_muon_iso_sf(iso, id, lep_fwkIdx, sysVar))

def get_leptons_SF(dilepton_object, id1, id2, iso1, iso2, sysVar = "nominal"):
    if noScaleFactors:
        return "1."

    lep1_obj = "hh_leptons[%s.ilep1]"%dilepton_object
    lep2_obj = "hh_leptons[%s.ilep2]"%dilepton_object
    
    lep1_sf = get_lepton_SF(lep1_obj, id1, iso1, sysVar)
    lep2_sf = get_lepton_SF(lep2_obj, id2, iso2, sysVar)

    return "%s * %s" % (lep1_sf, lep2_sf)
