"""
Automatically generate plotIt yml file from list of plots etc.
"""

def writePlotIt(plotList, outfile):
    for plot in plotList:
        if len(plot.variables) == 1:
            plotopts = {
                "x-axis"           : '"{0}"'.format(plot.axisTitles[0])
              , "y-axis"           : "Evt"
              , "y-axis-format"    : '"%1% / %2$.0f"'
              , "normalized"       : "false"
              , "x-axis-format"    : "[{0:e}, {1:e}]".format(plot.binnings[0].minimum, plot.binnings[0].maximum)
              , "log-y"            : "both"
              , "y-axis-show-zero" : "true"
              , "save-extensions"  : '["pdf"]'
              , "show-ratio"       : "true"
              , "sort-by-yields"   : "false"
              }
            plotopts.update(plot.plotopts) ## user can set everything, but the above defaults are always there
            frag = "\n".join([
                "'{name}':".format(name=plot.name)
              ]+[
                "  {0}: {1}".format(k,v) for k,v in plotopts.iteritems()
              ]+[''])
        outfile.write(frag)
