(TeX-add-style-hook "User guide"
 (lambda ()
    (LaTeX-add-labels
     "fig:RM_GUI"
     "sec-1"
     "sec-1-1"
     "sec-1-2"
     "sec-1-3"
     "sec-2")
    (TeX-run-style-hooks
     "hyperref"
     "amssymb"
     "wasysym"
     "marvosym"
     "textcomp"
     "amsmath"
     "ulem"
     "normalem"
     "rotating"
     "wrapfig"
     "float"
     "longtable"
     "graphicx"
     "fixltx2e"
     ""
     "fontenc"
     "T1"
     "inputenc"
     "utf8"
     "latex2e"
     "art11"
     "article"
     "11pt")))

