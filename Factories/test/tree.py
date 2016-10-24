extra_branches = ["weight"]

tree = {
        "name": "cool_tree",

        "cut": "!(jet_p4[0].Pt() < 20)",

        "branches": [

            {
                "name": "branch_1",
                "variable": "jet_p4[0].Pt()",
            },

            {
                "name": "weight_1",
                "variable": "common::combineScaleFactors<2>({{{0.5, 0.5}, {0.7, 0.3}}}, common::Variation::NOMINAL)",
            },

            {
                "name": "is_data",
                "variable": "event_is_data",
                "type": "bool",
            }

        ]

    }
