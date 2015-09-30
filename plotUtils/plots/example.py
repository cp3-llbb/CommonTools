plots = [{
            'name': 'dimuon_mass',
            'variable': 'hh_dimuons.M()',
            'plot_cut': '(hh_dimuons.M() > 20.) * event_weight',
            'binning': '(1000, 0, 1000)'
        }]
