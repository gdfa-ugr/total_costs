import pandas as pd

from . import mklbl as mklbl


miindex = pd.MultiIndex.from_product([mklbl('A',4),
                                       mklbl('B',2),
                                       mklbl('C',4),
                                       mklbl('D',2)])

