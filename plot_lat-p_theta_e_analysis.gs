function theana( args )
'reinit'
**-----------------------------------------------
**theta_e_analysis.gs
**Analysis of equivalent potential temperature with wind and vertical motion
**==============================================================================
rc=gsfallow('on')
_ivar='v1.0.0'

if( args = '' ) | ( subwrd(args,1) = '-help' ) | ( subwrd(args,1) = '-h' )
  help(); return
endif

***** Default values *****
lon_val = 120
time_val = '2006060900'
lat_min = 21
lat_max = 26
lev_min = 1000
lev_max = 700
output_dir = 'dnsave'
title_text = 'Theta_e,[v,w],w'
ensemble_num = 64
lon_range = 0.25
quit = 0

***** Argument parsing *****
* Required parameters
i=1
if( args != '' )
  time_val = subwrd(args,i) ; i=i+1
  if( subwrd(args,i) != '' )
    lon_val = subwrd(args,i) ; i=i+1
  endif
endif

** Optional parameters
arg = "dummy"
while( arg != "" )
  arg = subwrd( args, i )
  i = i + 1
  if( arg = '-lat')     ; lat_min=subwrd(args,i) ; lat_max=subwrd(args,i+1) ; i=i+2; endif
  if( arg = '-lev')     ; lev_min=subwrd(args,i) ; lev_max=subwrd(args,i+1) ; i=i+2; endif
  if( arg = '-outdir')  ; output_dir=subwrd(args,i) ; i=i+1; endif
  if( arg = '-title')   ; title_text=subwrd(args,i) ; i=i+1; endif
  if( arg = '-ensemble'); ensemble_num=subwrd(args,i) ; i=i+1; endif
  if( arg = '-lonrange'); lon_range=subwrd(args,i) ; i=i+1; endif
  if( arg = '-q'); quit=1 ; endif
endwhile

***** Main processing *****
say 'Processing theta_e analysis...'
say '    Time: 'time_val
say '    Longitude: 'lon_val
say '    Latitude range: 'lat_min' to 'lat_max
say '    Level range: 'lev_min' to 'lev_max

** Open data files
ifd = './extract_wrf_to_nc'
'xopen 'ifd'/eth.ctl'
'xopen 'ifd'/uvmet.ctl'
'xopen 'ifd'/wa.ctl'
'xopen -t ./CTL/sfc_Emean_surface.ctl'  ;** for loading ens. mean rainfall

** Set dimensions
'set lon 'lon_val
'set lat 'lat_min' 'lat_max
'set lev 'lev_min' 'lev_max
'set_ti 'time_val
'set e 1'

** Define averaged variables
lon_min = lon_val - lon_range
lon_max = lon_val + lon_range
p('define ethm = ave(ave(eth.1, lon='lon_min', lon='lon_max'),e=1, e='ensemble_num')')
p('define um = ave(ave(uvmet_u.2, lon='lon_min', lon='lon_max'),e=1, e='ensemble_num')')
p('define vm = ave(ave(uvmet_v.2, lon='lon_min', lon='lon_max'),e=1, e='ensemble_num')')
p('define wm = ave(ave(wa.3, lon='lon_min', lon='lon_max'),e=1, e='ensemble_num')')

'set dfile 4'
'set z 1'
p('define r6m = ave(rainnc.4(lev=10000, time+3hr) - rainnc.4(lev=10000, time-3hr), lon='lon_min', lon='lon_max')')

** Set up graphics
'set dfile 1'
'set lev 'lev_min' 'lev_max

'mgs'
'c'
'set parea 1.1 8.5 2 7.5'
'set xlint 1'
'set ylint 50'
'set ylopts 1 3 0.15'
'set xlopts 1 1 0'
'draw_dbg.gs 15'

** Plot equivalent potential temperature
'color 335 365 1 -kind rainbow2->indigo->fuchsia'
'd ethm'
'xcb_r ( -fs 5 -edge triangle ) -un [K] -pa 0.8'
'draw_b T:'time_val' tr 1 -co 1'
'draw_b Lo:'lon_val' tr 2 -co 1'

** Add vertical motion contours 
'set-off'
'set_gx c'
'set ccolor 4'
'set cmin 0.1'
'set cint 0.1'
'd wm'
'draw_b w>0.1 tr 3 -co 4'

** Add vectors
'vector2 vm (wm*100) 0.5 40 -sk 5,1'

** Final formatting and save
'draw-ol'
'draw_b [hPa] l 1 -an 90 -th 3 -pt 12pt'
'dtitle 'title_text' -dd 0'

** subfig 2
'set z 1'
gxh = qgxinfo('xmin')
gxo = qgxinfo('xmax')
gyh = qgxinfo('ymin')
gyo = qgxinfo('ymax')
** 定義子圖高度（可調整）
p2height = 1.2
p2margin = 0
** 設定 parea 將 ymin 往下移動
parea_ymin = gyh - p2height - p2margin
parea_ymax = gyh - p2margin
'set parea 'gxh' 'gxo' 'parea_ymin' 'parea_ymax''

'set_gx bar'
'set grid on'
'set ccolor 4'
'set vrange 0 130'
'set ylopts 1 3 0.15'
'set xlopts 1 3 0.15'
'set ylint 50'
'set xlint 1'
'd r6m'
'draw_b R6 l 1 -an 90 -th 3 -pt 12pt'
'draw-ol'


** Create output filename and save
if(output_dir != 'dnsave')
    output_filename = output_dir'/lat-p_'lon_val'_'time_val
    'savee2p 'time_val' -nn 'output_filename
    say 'Analysis completed. Output saved to: 'output_filename
    
endif

say 'Analysis completed.'

if(quit)
    'quit'
endif

return

***** Help function *****
function help()
say ''
say 'theta_e_analysis.gs - Analysis of equivalent potential temperature with wind and vertical motion'
say ''
say 'Usage:'
say '  theta_e_analysis <time> [longitude] [options]'
say ''
say 'Required parameters:'
say '  <time>        Time in format YYYYMMDDHH (e.g., 2006060900)'
say ''
say 'Optional parameters:'
say '  [longitude]   Longitude value (default: 120)'
say '  -lat <min> <max>     Latitude range (default: 21 26)'
say '  -lev <min> <max>     Level range in hPa (default: 1000 700)'
say '  -outdir <dir>        Output directory (default: output)'
say '  -title <text>        Title text (default: Theta_e,[v,w],w)'
say '  -ensemble <num>      Number of ensemble members (default: 64)'
say '  -lonrange <range>    Longitude averaging range (default: 0.25)'
say ''
say 'Examples:'
say '  theta_e_analysis 2006060900'
say '  theta_e_analysis 2006060900 120'
say '  theta_e_analysis 2006060900 120 -lat 20 25 -lev 1000 850'
say '  theta_e_analysis 2006060900 121 -outdir results -title Custom_Analysis'
say ''
return
