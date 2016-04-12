plots = [
        {
            'name': 'test_1',
            'variable': 'electron_p4[0].Pt()',
            'plot_cut': 'electron_p4.size() > 0',
            'binning': '(100, 0, 800)',
            'folder': 'my/nice/little/folder'
        },

        {
            'name': 'test_normalize_to',
            'variable': 'electron_p4[0].Pt()',
            'plot_cut': 'electron_p4.size() > 0',
            'binning': '(100, 0, 800)',
            "normalize-to": "pdf_up"
        },

        ]
