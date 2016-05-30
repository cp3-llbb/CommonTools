        __cut = ({{CUT}});
        if (__cut) {
            __weight = ({{WEIGHT}}) * __sample_weight;
            fill({{HIST}}.get(), {{VAR}}, __weight);
        }

