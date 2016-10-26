        __cut = ({{CUT}});
        if (__cut) {
            if (runOnMC) {
                __weight = ({{WEIGHT}}) * __sample_weight;
            } else {
                __weight = 1;
            }
            fill({{HIST}}.get(), {{VAR}}, __weight);
        }

