# The current dataset is accessible from the global variable 'dataset'
print dataset

# Any change made to this dict will be reflected into histFactory (very useful to change the output file name)

# Any options passed to the 'runs' are available as a 'options' dict global variable. If you look in the 'sample.json' file, you'll see it defines a 'tt_type' options.
print options

tt_type = None
if 'tt_type' in options:
    tt_type = options['tt_type']

# This directly change the name of the output file!
dataset["output_name"] += "_" + tt_type

# Add a plot based on the current tt decay type

cut = "(tt_gen_ttbar_decay_type "
if tt_type == "hadronic":
    cut += " == 1"
else:
    cut += " > 1"

cut += ')'

plots = [{
            'name': 'll_M_CAT_ElEl_IDMM_IsoLL',
            'variable': 'tt_diLeptons[ tt_diLeptons_IDIso[36][0] ].p4.M()',
            'plot_cut': '(((((elel_Category_IDMM_IsoLL_cut)&&(elel_Mll_IDMM_IsoLL_cut)&&(elel_DiLeptonTriggerMatch_IDMM_IsoLL_cut)&&(elel_DiLeptonIsOS_IDMM_IsoLL_cut)))&&(1)))*event_weight*' + cut,
            'binning': '(100, 0, 800)'
        }]
