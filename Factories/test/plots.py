headers = [
        'iostream'
        ]

code_before_loop = 'bool user_code = false;'
code_in_loop = 'user_code = true;'
code_after_loop = 'std::cout << "Added by user: " << user_code << std::endl;'

extra_branches = [
        'muon_p4'
        ]

optimize_plots = True

plots = [
        {
            'name': 'test_1',
            'variable': 'electron_p4[0].Pt()',
            'plot_cut': 'electron_p4.size() > 0',
            'binning': '(100, 0, 800)',
            'folder': 'my/nice/little/folder'
            },

        {
            'name': 'should_be_grouped_1',
            'variable': 'electron_p4[0].Pt()',
            'plot_cut': 'electron_p4.size() > 0',
            'weight': '2.5',
            'binning': '(100, 0, 800)',
            },

        {
            'name': 'should_be_grouped_2',
            'variable': 'electron_p4[0].Pt()',
            'plot_cut': 'electron_p4.size() > 0',
            'weight': '2.5',
            'binning': '(100, 0, 800)',
            },

        {
            'name': 'should_be_grouped_3',
            'variable': 'electron_p4[0].Pt()',
            'plot_cut': 'electron_p4.size() > 0',
            'weight': '2.5',
            'binning': '(100, 0, 800)',
            'allow-weighted-data': False
            },

        {
            'name': 'not_in_group',
            'variable': 'electron_p4[2].Pt()',
            'plot_cut': 'electron_p4.size() > 3',
            'weight': '2.5 * 5',
            'binning': '(100, 0, 800)',
            },

        {
            'name': 'test_normalize_to',
            'variable': 'electron_p4[0].Pt()',
            'plot_cut': 'electron_p4.size() > 0',
            'binning': '(100, 0, 800)',
            "normalize-to": "pdf_up"
            },

        {
            'name': 'entries',
            'variable': '1',
            'binning': '(2, 0, 2)',
            'plot_cut': 'true'
            }

        ]

sample_weights = {
        "test": "5.25",
        "test2": "muon_p4.size()"
        }

library_directories = [
        "/usr/lib",
        "/usr/lib64"
        ]

libraries = ['uuid', 'dl']
