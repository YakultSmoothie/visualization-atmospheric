DSET ^the_gra.nc
DTYPE netcdf
TITLE Equivalent potential temperature analysis - from /jet/ox/work/MYHPE/1/2025-0909-Frontal_env/00s/calc_WRF_ThetaE_Analysis.py
UNDEF -999.
PDEF  250 300 lccr  24.20537567138672 121.00436401367188    125.5 150.5    40.0 10.0 120.0    3000.0 3000.0
XDEF  296  LINEAR  117.038536  0.027027
YDEF  315  LINEAR  19.909378  0.027027
ZDEF 5 LEVELS 1000  990  875  850  825
TDEF 73 LINEAR 00z08jun2006 60mn
EDEF 64 NAMES 001 002 003 004 005 006 007 008 009 010 011 012 013 014 015 016 017 018 019 020 021 022 023 024 025 026 027 028 029 030 031 032 033 034 035 036 037 038 039 040 041 042 043 044 045 046 047 048 049 050 051 052 053 054 055 056 057 058 059 060 061 062 063 064

VARS 8
    eth=>eth       5  e,t,z,y,x  [K] Equivalent potential temperature
    dtedx=>dtedx   5  e,t,z,y,x  [K/m] Zonal gradient of equivalent potential temperature
    dtedy=>dtedy   5  e,t,z,y,x  [K/m] Meridional gradient of equivalent potential temperature
    absthe=>absthe 5  e,t,z,y,x  [K/m] Absolute gradient of equivalent potential temperature
    divg=>divg     5  e,t,z,y,x  [1/s] Horizontal divergence
    vort=>vort     5  e,t,z,y,x  [1/s] Relative vorticity
    XLAT=>xlat    0  y,x      [deg] Latitude
    XLONG=>xlon   0  y,x        [deg] Longitude
ENDVARS
