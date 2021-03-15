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

pro lrisbluebias, filename, prefix=prefix

	aaa=systime(/seconds)

	if n_elements(prefix) eq 0 then prefix='b'

        ; define gains from LRIS detectors site
        ;    (http://www2.keck.hawaii.edu/inst/lris/detectors.html)
        gain = [1.55, 1.56, 1.63, 1.70]
        gaindata = build_gaindata(gain)

        file = readmhdufits(filename,header=fhead,gaindata=gaindata,/linebias)

        ; get binning values
        binning = strcompress(sxpar(fhead,'BINNING'),/rem)
        xbin = strmid(binning,0,1)
        ybin = strmid(binning,2,1)

        ; default to entire chip (i.e. no spatial trimming)
	imgleft = 0
	imgright = 4095/xbin
        y1 = 0
        y2 = 4095/ybin

        grisname = strtrim(sxpar(fhead,'GRISNAME'))
        if grisname EQ '400/3400' then begin
           imgleft = 1460/xbin
           imgright = 2647/xbin
        endif
        if grisname EQ '300/5000' then begin
           imgleft = 1475/xbin
           imgright = 2662/xbin
        endif
        if grisname EQ 'clear' then begin
           imgleft = 305/xbin
           imgright = 3765/xbin
           y1 = 740/ybin
           y2 = 3300/ybin
        endif
        if grisname EQ '600/4000' then begin
           imgleft = 1460/xbin
           imgright = 2647/xbin
           slitname = strlowcase(strtrim(sxpar(fhead,'SLITNAME')))
           if strmid(slitname,0,4) NE 'long' then begin
              ;For masks
              imgleft = 0
              imgright = 4095/xbin
           endif
        endif

        tempimg = file[imgleft:imgright,y1:y2]
        delvarx, file
	newtempimg = transpose(tempimg)

        ; find chipgap and blotch it
        row_medians = median(newtempimg,dimension=1)
        gap_rows = WHERE(row_medians LE 0.5)
        ;print,gap_rows
        if gap_rows[0] NE -1 then begin
           for i=0,n_elements(gap_rows)-1 do newtempimg[*,gap_rows[i]] = 1.
        endif
        if n_elements(gap_rows) GT 10 then message,filename+' had '+strcompress(n_elements(gap_rows),/remove_all)+' rows with negative medians.',/continue

	sxaddpar, fhead, 'OBSERVAT', "keck"
        optpa, fhead

        time = round(sxpar(fhead, 'EXPTIME'))
        if time EQ 0. then time = round(sxpar(fhead, 'ELAPTIME'))
        sxaddpar, fhead, 'EXPTIME', time
        sxaddpar, fhead, 'EXPOSURE', time

        writefits, prefix+filename, newtempimg, fhead

	print,systime(/seconds)-aaa,' seconds to bias subtract ',filename

end
