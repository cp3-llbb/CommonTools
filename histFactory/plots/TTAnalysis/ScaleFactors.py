from TTAnalysis import TT

noScaleFactors = False

def lepton_id_to_string(wp):
    if wp == TT.LepID.L:
        return 'loose'
    elif wp == TT.LepID.M:
        return 'medium'
    elif wp == TT.LepID.T:
        return 'tight'

    raise Exception('Unknown lepton id working point')

def lepton_iso_to_string(wp):
    if wp == TT.LepIso.L:
        return 'loose'
    elif wp == TT.LepIso.T:
        return 'tight'

    raise Exception('Unknown lepton iso working point')

def btag_wp_to_string(wp):
    if wp == TT.BWP.L:
        return 'loose'
    elif wp == TT.BWP.M:
        return 'medium'
    elif wp == TT.BWP.T:
        return 'tight'

    raise Exception('Unknown b-tagging working point')

def get_muon_iso_sf_branch(iso, id):
    return 'muon_sf_iso_%s_id_%s' % (lepton_iso_to_string(iso), lepton_id_to_string(id))

def get_muon_id_sf_branch(id):
    return 'muon_sf_id_%s' % (lepton_id_to_string(id))

def get_csvv2_sf_branch(wp):
    return 'jet_sf_csvv2_%s' % (btag_wp_to_string(wp))

# Lepton scale factors

def get_dilepton_object(dilepton_index, id1, id2, iso1, iso2):
    return 'tt_diLeptons[tt_diLeptons_IDIso[%d][%d]]' % (TT.LepLepIDIso(id1, iso1, id2, iso2), dilepton_index)

def get_lepton_SF_for_dilepton(lepton_index, dilepton_index, id1, id2, iso1, iso2):
    if noScaleFactors:
        return "1."

    pair_field = None
    if lepton_index == 0:
        pair_field = 'first'
    else:
        pair_field = 'second'

    dilepton_object = get_dilepton_object(dilepton_index, id1, id2, iso1, iso2)

    lepton_index = '%s.lidxs.%s' % (dilepton_object, pair_field)
    lepton_object = 'tt_leptons[%s]' % lepton_index

    lepton_id_sf = '(({0}.isEl) ? 1. : {1}[{0}.idx][0])'.format(lepton_object, get_muon_id_sf_branch(id1))
    lepton_iso_sf = '(({0}.isEl) ? 1. : {1}[{0}.idx][0])'.format(lepton_object, get_muon_iso_sf_branch(iso1, id1))

    return '%s * %s' % (lepton_id_sf, lepton_iso_sf)

def get_leptons_SF_for_dilepton(dilepton_index, id1, id2, iso1, iso2):
    return '%s * %s' % (get_lepton_SF_for_dilepton(0, dilepton_index, id1, id2, iso1, iso2), get_lepton_SF_for_dilepton(1, dilepton_index, id1, id2, iso1, iso2))

# b-tagging scale factors

def get_dijet_object(dijet_index, b1_wp, b2_wp, id1, id2, iso1, iso2):
    return 'tt_diJets[tt_diLepDiJets[tt_diLepDiBJets_DRCut_BWP_CSVv2Ordered[%d][%d]].diJetIdx]' % (TT.LepLepIDIsoJetJetBWP(id1, iso1, id2, iso2, b1_wp, b2_wp), dijet_index)

def get_at_least_two_b_SF_one_b_for_dijet(b_index, dijet_index, b1_wp, b2_wp, id1, id2, iso1, iso2):
    if noScaleFactors:
        return "1."

    pair_field = None
    if b_index == 0:
        pair_field = 'first'
    else:
        pair_field = 'second'

    dijet_object = get_dijet_object(dijet_index, b1_wp, b2_wp, id1, id2, iso1, iso2)

    return '%s[%s.idxs.%s][0]' % (get_csvv2_sf_branch(b1_wp), dijet_object, pair_field)

def get_at_least_two_b_SF_for_dijet(dijet_index, b1_wp, b2_wp, id1, id2, iso1, iso2):
    first_bjet_sf  = get_at_least_two_b_SF_one_b_for_dijet(0, dijet_index, b1_wp, b2_wp, id1, id2, iso1, iso2)
    second_bjet_sf = get_at_least_two_b_SF_one_b_for_dijet(1, dijet_index, b1_wp, b2_wp, id1, id2, iso1, iso2)

    return "%s * %s" % (first_bjet_sf, second_bjet_sf)
