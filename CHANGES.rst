Changelog of lizard-waterregime
===================================================


0.3.4 (unreleased)
------------------

- Nothing changed yet.


0.3.3 (2011-07-11)
------------------

- Conformed code to pyflakes / pep8

- Solved problems with date selector.


0.3.2 (2011-04-20)
------------------

- Implemented nearest() method in calculator to extend evap range


0.3.1 (2011-04-20)
------------------

- Changed the p-e-unknown color to gray.

- Margin for graph determined from axes.dataLim attribute 

- Fixed not-updating mapcolors bug.


0.3 (2011-04-19)
----------------

- Changed layers to use shapefiles rather than postgres spatial database

- Added various help functions to models


0.2.2 (2011-04-11)
------------------

- Removed timeseries dependency


0.2.1 (2011-04-11)
------------------

- Fixed scaling bug on graph when events contain NaNs.

- Fixture zzl_waterregime extended with precipitationsurplus records.

- Bugfixed multithreading bug in calculator.py. Performance is improved
  as a side-effect.


0.2 (2011-04-11)
----------------

- Switched to Oracle.

- Implemented calculator.

- Improved graphs.

- Added admin pages.

- Added South.


0.1 (2011-03-24)
----------------

- Initial library skeleton created by nensskel

- Implemented AdapterWaterregime with legend, hover and popup

- Models extended for timeseries functionality
