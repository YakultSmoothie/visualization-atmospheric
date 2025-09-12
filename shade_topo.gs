'reinit '
'set display color white'
'c'
'xopen /jet/ox/DATA/ETOPO1/etopo1_ice_g_f4-slrain.nc'  ;**提供地形高度(hgt)

'set rgb 96 199 239 239'
'set rgb 97 50 220 100'

'set clevs 0'
'set ccols 96 97'
'set gxout shade2'
'set mpdraw off'
'd hgt.1'

'set gxout contour'
'set ccols 1'
'set clevs 0'
'set clab off'
'd hgt.1'

'printim shade_topo.gs.png png x1100 y850'
'quit'

