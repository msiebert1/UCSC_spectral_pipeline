# Wed 09:40:34 19-Feb-2020
begin	identify ARC_red.ms - Ap 1
	id	ARC_red.ms
	task	identify
	image	ARC_red.ms - Ap 1
	aperture	1
	aplow	20.18
	aphigh	25.82
	units	Angstroms
	features	8
	         18.59 5460.73882    5460.74   4.0 1 1 Hg I     *
	        300.07 6143.07138    6143.06   4.0 1 1 Ne I     *
	        447.19 6506.50809    6506.53   4.0 1 1 Ne I     *
	        657.44 7032.45278    7032.41   4.0 1 1 Ne I     *
	        713.54 7173.90457    7173.94   4.0 1 1 Ne I     *
	        818.22 7438.90439     7438.9   4.0 1 1 Ne I     *
	       1231.33 8495.35998    8495.36   4.0 1 1 Ne I     *
	       1870.15    10139.5    10139.5   4.0 1 1 Hg I     *
	function spline3
	order 3
	sample *
	naverage 1
	niterate 0
	low_reject 3.
	high_reject 3.
	grow 0.
	coefficients	10
		3.
		3.
		1.
		2217.
		617.4377962141928
		899.1320739305894
		1204.777436563001
		1521.671420415141
		1840.959901477776
		2113.625309753321

