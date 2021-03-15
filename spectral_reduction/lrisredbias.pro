;-----------------------------------------------------------------------
function build_gaindata, gain
;-----------------------------------------------------------------------
; convert gain into a structure...
;-----------------------------------------------------------------------
n = n_elements(gain)
vidinp = ['VidInp1','VidInp2','VidInp3','VidInp4']

foo = {GAINDATA, vidinp:'',gain:0.}
gaindata = replicate({GAINDATA}, n)
for i=0,n-1 do begin
    gaindata[i] = {GAINDATA, vidinp:vidinp[i], gain:gain[i]}
endfor 

return, gaindata
end

pro lrisredbias, filename, prefix=prefix

	aaa=systime(/seconds)

	if n_elements(prefix) eq 0 then prefix='b'

        ; define gains guessed from a ratio of flats of amps 1 and 4 from 20090617
        ;gain = [1.25, 1., 1., 1.]
        ; define gains from email from Marc Kassis to Jeff Silverman -- 20090707
        gain = [1.022, 0.955, 0.877, 0.916]
        gaindata = build_gaindata(gain)

        file = readmhdufits(filename,header=fhead,gaindata=gaindata,/linebias)

        ; get binning values
        binning = strcompress(sxpar(fhead,'BINNING'),/rem)
        xbin = float(strmid(binning,0,1))
        ybin = float(strmid(binning,2,1))

        graname = strtrim(sxpar(fhead,'GRANAME'))
        pane = strcompress(sxpar(fhead,'PANE'),/rem)

        ; Fix the enormous number of bad columns
        if pane EQ '0,0,4096,4096' then begin
           file[(730-1)/xbin,(1570/ybin):*] =  (file[(729-1)/xbin,(1570/ybin):*] + file[(731-1)/xbin,(1570/ybin):*])/2
           file[(791-1)/xbin,(2974/ybin):*] =   file[(789-1)/xbin,(2974/ybin):*]
           file[(792-1)/xbin,(2974/ybin):*] =   file[(790-1)/xbin,(2974/ybin):*]
           file[(793-1)/xbin,(1560/ybin):*] =   file[(795-1)/xbin,(1560/ybin):*]
           file[(794-1)/xbin,(1027/ybin):*] =   file[(796-1)/xbin,(1027/ybin):*]
           file[(798-1)/xbin,(474/ybin):*] =   (file[(797-1)/xbin,(474/ybin):*] + file[(799-1)/xbin,(474/ybin):*])/2
           file[(832-1)/xbin,(946/ybin):*] =    file[(831-1)/xbin,(946/ybin):*]
           file[(833-1)/xbin,(946/ybin):*] =    file[(834-1)/xbin,(946/ybin):*]
           file[(868-1)/xbin,(3003/ybin):(3040/ybin)] =  (file[(867-1)/xbin,(3003/ybin):(3040/ybin)] + file[(869-1)/xbin,(3003/ybin):(3040/ybin)]) / 2
           file[(887-1)/xbin,(2970/ybin):*] =  (file[(886-1)/xbin,(2970/ybin):*] + file[(888-1)/xbin,(2970/ybin):*]) / 2
           file[(928-1)/xbin,(1096-1)/ybin] =    (file[(927-1)/xbin,(1096-1)/ybin] + file[(929-1)/xbin,(1096-1)/ybin])/2
           file[(942-1)/xbin,(1767/ybin):*] =    file[(940-1)/xbin,(1767/ybin):*]
           file[(943-1)/xbin,(1767/ybin):*] =    file[(941-1)/xbin,(1767/ybin):*]
           file[(944-1)/xbin,(1767/ybin):*] =   (file[(941-1)/xbin,(1767/ybin):*] + file[(946-1)/xbin,(1767/ybin):*])/2
           file[(945-1)/xbin,(1767/ybin):*] =    file[(946-1)/xbin,(1767/ybin):*]
           file[(959-1)/xbin,(1560/ybin):*] =   file[(958-1)/xbin,(1560/ybin):*]
           file[(960-1)/xbin,(1560/ybin):*] =   file[(961-1)/xbin,(1560/ybin):*]
           file[(983-1)/xbin,(812/ybin):*] =   (file[(982-1)/xbin,(812/ybin):*] + file[(984-1)/xbin,(812/ybin):*])/2
           file[(1005-1)/xbin,(3849/ybin):(3859/ybin)] = (file[(1004-1)/xbin,(3849/ybin):(3859/ybin)] + file[(1006-1)/xbin,(3849/ybin):(3859/ybin)])/2
           file[(1039-1)/xbin,(1019/ybin):*] = (file[(1038-1)/xbin,(1019/ybin):*] + file[(1040-1)/xbin,(1019/ybin):*])/2
           file[(1049-1)/xbin,(1016/ybin):*] = (file[(1048-1)/xbin,(1016/ybin):*] + file[(1050-1)/xbin,(1016/ybin):*])/2
           file[(1100-1)/xbin,(1469/ybin):(1474/ybin)] = file[(1099-1)/xbin,(1469/ybin):(1474/ybin)]
           file[(1101-1)/xbin,(1469/ybin):(1474/ybin)] = file[(1099-1)/xbin,(1469/ybin):(1474/ybin)]
           file[(1101-1)/xbin,(1475/ybin):*] =    file[(1100-1)/xbin,(1475/ybin):*]
           file[(1102-1)/xbin,(1469/ybin):*] =    file[(1103-1)/xbin,(1469/ybin):*]
           file[(1148-1)/xbin,(2350/ybin):*] =    file[(1146-1)/xbin,(2350/ybin):*]
           file[(1149-1)/xbin,(2350/ybin):*] =    file[(1147-1)/xbin,(2350/ybin):*]
           file[(1150-1)/xbin,(2350/ybin):*] =    file[(1147-1)/xbin,(2350/ybin):*]
        endif

        ; default to entire chip (i.e. no spatial trimming)
	imgleft = 0
	imgright = 4095/xbin
        y1 = 0
        y2 = 4095/ybin

        if graname EQ '1200/7500' then begin
           imgleft = 40/xbin
           imgright = 1110/xbin
              if pane EQ '0,0,4096,4096' then begin
                 imgleft = 1564/xbin
                 imgright = 2646/xbin
              endif
        endif
        if graname EQ '831/8200' then begin
           imgleft = 53/xbin
           imgright = 1123/xbin
        endif
        if graname EQ '600/5000' then begin
           imgleft = 53/xbin
           imgright = 1123/xbin
        endif
        if graname EQ '600/7500' then begin
           imgleft = 56/xbin
           imgright = 1138/xbin
           slitname = strlowcase(strtrim(sxpar(fhead,'SLITNAME')))
           if strmid(slitname,0,4) NE 'long' then begin
              ;For masks
              imgleft = 1
              imgright = 1
           endif else begin
              ;For morons who read out the whole chip in longslit mode
              if pane EQ '0,0,4096,4096' then begin
                 imgleft = 1564/xbin
                 imgright = 2646/xbin
              endif
           endelse
        endif
        if graname EQ 'mirror' then begin
;;            imgleft = 401/xbin
;;            imgright = 3785/xbin
;;            y1 = 648/ybin
;;            y2 = 3264/ybin
;;            y2 = 2499
;;            imgright = 3399
           if pane EQ '0,0,4096,4096' then begin
              imgleft = 400/xbin
              imgright = (400+3400-1)/xbin
              y1 = 625/ybin
              y2 = (625+2500-1)/ybin
           endif
           if pane EQ '400,625,3400,2500' then begin
              imgleft = 0
              imgright = (3400-1)/xbin
              y1 = 0
              y2 = (2500-1)/ybin
           endif
           if pane EQ '1500,0,1200,4096' then begin
              imgleft = 2/xbin
              imgright = 1198/xbin
           endif
        endif
        if graname EQ '400/8500' then begin
           imgleft = 66/xbin
           imgright = 1136/xbin
           slitname = strlowcase(strtrim(sxpar(fhead,'SLITNAME')))
           if strmid(slitname,0,4) NE 'long' then begin
              ;For masks
              imgleft = 265/xbin
              imgright = 3837/xbin
           endif else begin
              ;For morons who read out the whole chip in longslit mode
              pane = strtrim(sxpar(fhead,'PANE'))
              if pane EQ '0,0,4096,4096' then begin
                 imgleft = 1580/xbin
                 imgright = 2650/xbin
              endif
           endelse
        endif

        ; for bizarre pane section from Perley from 20100207
        ; also had to add a chunk to the beginning and end to 
        ;   make it line up with the rest of the data
        ;imgleft = 1580-400
        ;imgright = 2650-400
        ;y1 = 0
        ;y2 = 2499

	tempimg = file[imgleft:imgright,y1:y2]
	delvarx, file
        newtempimg = transpose(tempimg)

        ; find chipgap and blotch it
        ; find bad rows (in bottom half of chip) and blotch them
        row_medians = median(newtempimg,dimension=1)
        gap_rows2 = WHERE(row_medians LE 0.5)
        for i=0,n_elements(gap_rows2)-1 do newtempimg[*,gap_rows2[i]] = 1.
        ;if n_elements(gap_rows) GT 10 then message,filename+' had '+strcompress(n_elements(gap_rows),/remove_all)+' rows with negative medians.',/continue
        ;print,gap_rows2

	sxaddpar, fhead, 'OBSERVAT', "keck"
        optpa, fhead

        time = round(sxpar(fhead, 'EXPTIME'))
        if time EQ 0. then time = round(sxpar(fhead, 'ELAPTIME'))
        sxaddpar, fhead, 'EXPTIME', time
        sxaddpar, fhead, 'EXPOSURE', time

        writefits, prefix+filename, newtempimg, fhead

	print,systime(/seconds)-aaa,' seconds to bias subtract ',filename

end
