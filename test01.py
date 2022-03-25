import PythonMagick as pm
import base64
import numpy as np
import struct
import cv2




############################################################
def shadow(BGcol,sigma,opacity,myimg,offx,offy):

    # The object must be placed on a transparent background
    # The image will be resized such that width and height will increase
    # by the amount (sigma x 4)  (i.e. size = (w + (sigma *4)) x (h + (sigma * 4))
    # to accomodate the spread out blurred edges if present on the original image
    # edge.
 
    opscale=opacity/100.0
    #print("opscale="+str(opscale))

    # Increase the background size to accomodate the blur edges which spread outwards
    gcan=pm.Geometry(int(myimg.size().width()+(sigma*4)), int(myimg.size().height()+(sigma*4)))  
    img2=pm.Image(gcan,'none') 
    gt=pm.GravityType.CenterGravity
    co=pm.CompositeOperator.SrcOverCompositeOp
    img2.composite(myimg,gt,co)

    #img2.write("test.png");exit(0) # OK size increases

    #print("opscale="+str(opscale))
    #img2=pm.Image(img) # Same size copy is wrong because blur is likely to cause increase in image size
    img2.blur(80,sigma)
    #img2.gaussianBlur(80,5) # Very Slow
    imgT=pm.Image(img2.size(),BGcol)
    gt=pm.GravityType.CenterGravity
    co=pm.CompositeOperator.CopyOpacityCompositeOp
    imgT.composite(img2,gt,co)
    #imgT.write('imgT1.png')
    
    cimg=pm_to_cv2(imgT)
    #print(opacity/100);exit(0)
    cimg[:,:,3] = cimg[:,:,3] * opscale
    cimg[:,:,3] = np.uint8(cimg[:,:,3])
    imgT=cv2_to_pm(cimg)
    imgT.magick('PNG')
   # imgT.write('imgT2.png')
   # return imgT
#    exit(0)
    imgR=pm.Image(imgT.size(),'none')
    co=pm.CompositeOperator.SrcOverCompositeOp
    gstr=''
    if offx > 0 :
        gstr += '-'
    else :
        gstr += '+'

    gstr += str(offx)

    if offy > 0 :
        gstr += '-'
    else :
        gstr += '+'

    gstr += str(offy)
    
    imgR.composite(imgT,gstr,co)
    imgR.magick('PNG')
    return imgR
############################################################ 
def cv2_to_pm(cvimg):
    NC=cvimg.shape[2]
    Wd=cvimg.shape[1]
    Ht=cvimg.shape[0]
    #print("Ht=%d Wd=%d" %(Ht, Wd))#;exit(0)
    #print("NC="+str(NC))

    # Assuming NC=4
    nab=cvimg[:,:,0]
    nag=cvimg[:,:,1]
    nar=cvimg[:,:,2]
    naa=cvimg[:,:,3]
    na2=np.dstack((nar,nag,nab,naa))
    na2=np.uint8(na2)
    na2=na2.reshape(-1)
    #print(na2.tobytes());exit(0)
    b=pm.Blob()
    b.data=na2.tobytes()
    #print(b.length())
    pimg=pm.Image()
    pimg.size(str(Wd)+'x'+str(Ht))
    pimg.depth(8)
    pimg.magick('rgba')
    pimg.read(b)
    return pimg

def pm_to_cv2(myimg):
    
    b=pm.Blob()
    
    # Works as 2nd arg to write
    # 'h', 'text', 'txt', 
    myimg.write(b,'rgba')
    #myimg.write(b,'png') # able to use read() with this format
    # When pm.Blob.data is binary use pm.Blob.base64() to 
    # access the binary data

    # Use of read()
    # must specify size, magick('RGBA') and depth else "unexpected EOF error" is thrown
   # myimg2=pm.Image();myimg2.magick('RGBA');myimg2.depth(8);
#    myimg2.size('500x500');myimg2.read(b);myimg2.display();exit(0)

    mydata=base64.b64decode(b.base64())

    #print("b.length()="+str(b.length()))

    dep=myimg.depth()
    
    if  dep== 8:
    	FC='B' # Format Character
    elif dep == 16:
    	FC='H' 
    else :
    	print("Unknown image depth : "+str(dep))
    	exit(0)

    #print("FC="+FC)

    NC=None
    # Number of channels
    # img.colorSpace() will show
    # PythonMagick._PythonMagick.ColorspaceType.sRGBColorspace
    	
    # Value returned by magick() changes after call to write() 
    if myimg.magick() == 'RGB': 
    	NC=3
    elif myimg.magick() == 'RGBA' :
    	NC=4
    if NC == None:
    	print("Number of channels cannot indentified")
    	exit(0)

    #print("NC="+str(NC))

    # Img Size
    ht=myimg.rows()
    wd=myimg.columns()

    #print("ht=%d wd=%d" %(ht,wd))

    #myupd=struct.unpack('H'*500*500*3,mydata) #Unpacked data
    #myupd=struct.unpack('750000H',mydata) #Unpacked data
    myupd=struct.unpack(str(ht*wd*NC)+FC,mydata) #Unpacked data
    
    na=np.array(myupd)
    na=na.reshape((ht,wd,NC))
    nar=na[:,:,0]
    nag=na[:,:,1]
    nab=na[:,:,2]
    naa=na[:,:,3]

    na2=np.dstack((nab,nag,nar,naa))
    if FC == 'H':
        na2 = na2 / 256
#    print(na2)
    na2=np.uint8(na2)
    return na2
############################################################

#                STAR OF MAIN




ovrOff=None

def cyl_prog(PER):

    global ovrOff
# 100 %
#P1=263

# 0 %
#P1=16
    P1=16+int((263-16)*PER/100)
    P2=P1+40
   # print("P1=%d P2=%d" % (P1,P2));return None;
    
    img=pm.Image()
    img.size('320x90')
    img.read('xc:none')
    
    imp=pm.Image()
    imp.size('1x90')
  #  imp.read('gradient:white-snow4')
    #imp.read('gradient:orchid-DarkSalmon')
    imp.read('gradient:yellow-brown')

    
    
    img.fillPattern(imp)
    img.strokeColor('snow4')
    img.draw(pm.DrawableRoundRectangle(16,5,304,85,20,40)) # 1
    #img.write('png32:cyl01.png')
    #exit(0)
    ##################################
    img.fillPattern(pm.Image())# reset
    img.fillColor('SlateGray1')
    img.draw(pm.DrawableRoundRectangle(264,5,304,85,20,40)) # 2
    #img.write('png32:cyl02.png')
    ##################################
   # imp.read('gradient:chartreuse-green')
    imp.read('gradient:fuchsia-plum1')
    img.fillPattern(imp)
    img.draw(pm.DrawableRoundRectangle(16,5,P2,85,20,40)) # 3
    #img.write('png32:cyl03.png')
    ##################################
#    imp.read('gradient:chartreuse1-chartreuse3')
    imp.read('gradient:red-orange')
    img.fillPattern(imp)
    img.draw(pm.DrawableRoundRectangle(P1,5,P2,85,20,40)) # 4
    #img.write('png32:cyl04.png')
    ##################################
    img.fillPattern(pm.Image())
    img.fillColor('transparent')
    img.draw(pm.DrawableRoundRectangle(264,5,304,85,20,40)) # 5
    #img.write('png32:cyl05.png')
    ##################################
    img.strokeWidth(2)
    img.draw(pm.DrawableRoundRectangle(16,5,304,85,20,40)) # 6
    #img.write('png32:cyl06.png')
    ##################################
    cyl_img=shadow('snow4',3,80,img,3,3)
    co=pm.CompositeOperator.SrcOverCompositeOp
    cyl_img.composite(img,img.size(),co)
    #cyl_img.write('png32:shadow.png')
    ##################################
    img=pm.Image()
    img.backgroundColor('none')
    img.font('Helvetica') #not monospaced shaky
    #img.font('DejaVu-Sans-Mono') #not monospaced shaky
    #img.font('Bitstream-Vera-Sans-Mono')
    img.fontPointsize(70)
    img.strokeWidth(1)
   # img.fillColor('red')
    img.fillColor('blue')
    img.read('label:%3d' % PER )
    img.trim()
    img.page(img.size())

    #img.display()
    #img.write("text.png")
   # imgS=shadow('firebrick3',3,80,img,3,3)
    imgS=shadow('navy',3,80,img,3,3)
    co=pm.CompositeOperator.SrcOverCompositeOp
    gt=pm.GravityType.NorthGravity
   # imgS.composite(img,img.size(),co)
    imgS.composite(img,gt,co)

    imgS1=pm.Image(imgS) # Number
    #imgS.write('text_shadow.png')
    
   # imgS.display()
    
    img.read('label:%%')
    img.trim()
    img.page(img.size())

    #img.display()
    #img.write("text.png")
   # imgS=shadow('firebrick3',3,80,img,3,3)
    imgS=shadow('navy',3,80,img,3,3) # "%" sign

    co=pm.CompositeOperator.SrcOverCompositeOp
    gt=pm.GravityType.NorthGravity
   # imgS.composite(img,img.size(),co)
    imgS.composite(img,gt,co)
    #imgS.write('test2.png')
    #imgS.display()
    #exit(0)
    #perc=pm.Image(imgS.size(),'white')
    #perc.composite(imgS,imgS.size(),co)
    #perc.display()
    
    csize=pm.Geometry( cyl_img.size().width() , cyl_img.size().height() + imgS.size().height() )
    #print(cyl_img.size().width() , cyl_img.size().height());exit(0);
 #   canvas=pm.Image(csize,'white') # Probably csize varies hence shaky
    canvas=pm.Image('340x180','white')
    
    if ovrOff == None:
      ovrOff=pm.Geometry(csize)
      
     # ovrOff.xOff( int(cyl_img.size().width()/2 - imgS.size().width()/2 ) )
     # ovrOff.yOff( cyl_img.size().height() )
      #ovrOff.yOff( imgS.size().height() ) # shaky
      ovrOff.yOff(70)
      ovrOff.xNegative(False)
      ovrOff.yNegative(False)

    co=pm.CompositeOperator.SrcOverCompositeOp
#    canvas.composite(cyl_img,ovrOff,co)
    canvas.composite(cyl_img,'+0-70',co) 
  
    
   # canvas.composite(imgS,pm.GravityType.NorthGravity,co)
    #canvas.composite(imgS,pm.GravityType.NorthEastGravity,co)
    canvas.composite(imgS1,'-75-5',co)
    canvas.composite(imgS,'-185-5',co)
    #canvas.display()
    #exit(0)
    return canvas



fourcc = cv2.VideoWriter_fourcc(*'XVID')
#fourcc = cv2.VideoWriter_fourcc(*'MPNG') # Not working on transparent BG
out = cv2.VideoWriter('cyl_prog.avi',fourcc, 20.0, (640,480))

bg_can=pm.Image('640x480','white')
#bg_can=pm.Image('640x480','none')

gt=pm.GravityType.CenterGravity
co=pm.CompositeOperator.SrcOverCompositeOp

#for i in range(100,111):
for i in range(101):
	cyl=cyl_prog(i)
	#continue
	bg_can.composite(cyl, gt,co)	
	frame=pm_to_cv2(bg_can)
	frame=frame[:,:,0:3]# Remove the alpha channel for video creation
#	print(frame.dtype);print(frame.shape);break;
	#cyl.display()
	#cv2.imshow('frame',frame)
	#if cv2.waitKey(0) & 0xFF == ord('q'):
	#	break
        #
	#break

	if i == 0 or i == 100 :
		j=40 # 2 sec intro and outro
	else :
		j=2
 	
	for k in range(j):
		out.write(frame)
	print("\rProgress : %d %%" %(i),end='')

print(".. done")
out.release()




