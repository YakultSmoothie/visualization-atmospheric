'reinit'
rc = gsfallow('on')

;** 定義陸地遮罩 - 讀取EC不變場資料
'allclose'
'define-chp.gs 850 EC /DATA/EC/era_invariant_0.5.grib.ctl'


;** 開啟月平均氣候場資料 (1979-2022)
'allclose'
'xopen /1979-2022/M.ctl'
'set lev 850'
;** 定義氣候平均場變數
'define qm = c1 * 1000'     ;** 比濕轉換為 g/kg
'define zm = a1 / 9.81'     ;** 位勢高度轉換為 gpm
'define um = d1'            ;** u 風分量
'define vm = e1'            ;** v 風分量


;** 開啟2006年5-6月ERA5資料
'allclose'
'xopen /ERA5/M05-06/2006.pre.nc'
'set lev 850'
;** 計算2006年5月15日-6月15日平均場
'define q2006 = ave(q.1 * 1000, time=00z15may2006, time=18z15jun2006)'
'define z2006 = ave(z.1 / 9.81, time=00z15may2006, time=18z15jun2006)'
'define u2006 = ave(u.1, time=00z15may2006, time=18z15jun2006)'
'define v2006 = ave(v.1, time=00z15may2006, time=18z15jun2006)'

;** 計算異常場 (2006年 - 氣候平均) 並套用陸地遮罩
'define qdiff = (q2006 - qm) * chp'    ;** 比濕異常
'define zdiff = (z2006 - zm) * chp'    ;** 位勢高度異常
'define udiff = (u2006 - um) * chp'    ;** u風異常
'define vdiff = (v2006 - vm) * chp'    ;** v風異常

;** 開始繪圖設定
'mgs'
'c'
'set-scale 8,7 -xi 1 -yi 1'    ;** 設定圖幅大小與位置
'set xlint 20'                 ;** 經度網格間距
'set ylint 10'                 ;** 緯度網格間距
'draw_dbg.gs 15'               ;** gray brackground

;** 繪製q異常shd
'color -2 2 0.4 -kind bluered2'    ;** 設定色標 (-2到2, 間距0.4, 藍紅配色)
'set grads off'
'd qdiff'
'xcb_r ( ) -po r -pa 0.6 -un [g/kg]'    ;** 右側色標，單位g/kg

;** 疊加地圖
'set line 1 1 5'               ;** 設定線條樣式
'draw map'

;** 等值線
'set-off'
'cint4 zdiff 5 -co 3 -ct 3'    ;** 位勢高度異常等值線，間距5，綠色
'vector2 udiff vdiff 0.4 10 -co 0,9 -un [m/s]'    ;** 風場向量
'draw-ol.gs'                   ;** 繪製海岸線

;** 添加標題
'dtitle q[(Y06-CM),850] -co 1 -yo 0.1'    ;** 圖標題：2006年與氣候平均差值，850hPa

;** 保存圖片
'savee2p -nn output/plot_anomaly/plot_2006_850hPa_anomaly -q'
