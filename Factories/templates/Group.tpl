        // New group
        __cut = ({{CUT}});
        if (__cut) {
{{#NO_WEIGHTS_ON_DATA}}
            if (runOnMC) {
{{/NO_WEIGHTS_ON_DATA}}
                __weight = ({{WEIGHT}}) * __sample_weight;
{{#NO_WEIGHTS_ON_DATA}}
            } else {
                __weight = 1;
            }
{{/NO_WEIGHTS_ON_DATA}}

            {{PLOTS}}
        }
        // End of group
