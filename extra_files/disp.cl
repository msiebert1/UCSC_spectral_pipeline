procedure disp(inlist,reference)

# Script to dispersion correct a list a files with a given reference image
# all it does is elimate the annoyance of having to hedit the
# file before doing a dispcor
# 05/2001  RC
# 0 is considered to be log , and 1 to be linear
# 03/2023  KT 

string	inlist		{prompt="Image(s) for dispersion correction"}
string	reference	{prompt="Reference image"}
string	prefix		{"d",prompt="Prefix for output images"}
int	    linear		{1,prompt="use 0 if reducing esi"}

struct	*inimglist

begin

	string 	infile, img

	infile =  mktemp("tmp$lick")
	sections (inlist,option="fullname",>infile)
	inimglist = infile


	
	while (fscan(inimglist,img) != EOF) {
	      
          if (linear == 0) {
            printf("Applying ESI linear wavelength solution \n");
            #dispcor(img,prefix // img,ignoreaps = yes,linearize = no,log=yes);
            hedit(img,"REFSPEC1",reference,del+,add+,ver-,show+);
            #dispcor(img,prefix // img,ignoreaps+,linearize-,log+);
            dispcor(img,prefix // img,ignoreaps+);
          } else {
          	hedit(img,"REFSPEC1",reference,del+,add+,ver-,show+);
          	dispcor(img,prefix // img);
          }

	}

	inimglist = ""


end
