Benchmark parsers

Simple output parsers for select benchmarks that CHPC uses written in Python (NumPy, Pandas).

Benchmark output files are expected to be named with suffixes indicating CPU count, run count and, optionally, input file name and/or size.

The parsers scan through these output files finding keyworded lines with the performance measures (specific for each benchmark), parse out the value(s) of interest and create summary csv and txt files with all the values, means and stds.

