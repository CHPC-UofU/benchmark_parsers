import string
import sys
import time
import glob
import subprocess
import numpy as np
import pandas as pd

def getKey(filename):
  return filename.split(".")[3]


# find all output files
myfiles=glob.glob('inv.out.*')
myfiles=sorted(myfiles,key=getKey)
print(myfiles)
#cpus=sorted(set([x.split(".")[2] for x in myfiles]),key=int)
#cpus and threads need to be order preserving
mylist=[i.split('.')[3] for i in myfiles]
cpus=[]
[cpus.append(item) for item in mylist if item not in cpus]
mylist=[i.split('.')[2] for i in myfiles]
threads=[]
[threads.append(item) for item in mylist if item not in threads]
#cpus=set([x.split(".")[3] for x in myfiles])
#threads=set([x.split(".")[2] for x in myfiles])
runs=sorted(set([x.split(".")[4] for x in myfiles]),key=int)
init='Input files read'
rxbkg='receiver background'
dombkg='domain fields'
domgrn='domain Greens tensors'
firstmod='supplied initial model'
frechet='Frechet time'
total='Total time'

mybench=['Rx background fields','Domain background fields','Domain Greens tensors','First modeling','Frechet','Total modeling','Total runtime'];

# create array for all results
allres=np.zeros([len(mybench),len(cpus),len(runs)],order='F')
print('CPUs',cpus)
print('Threads',threads)
print('Runs',runs)
print('Metrics',mybench)

cpu=32
thread=1
run=1

# loop over all results and fill in the results data array
for ic, cpu in enumerate(cpus):
 for ir, run in enumerate(runs):
   thread=list(threads)[ic]
   filename='inv.out.'+`thread`+'.'+`cpu`+'.'+`run`
   print(filename)
   proc = subprocess.Popen('grep \"'+init+'\" '+filename,shell=True,stdout=subprocess.PIPE,bufsize=1, universal_newlines=True)
   output=proc.stdout.read()
   res=output.split(" ")
   if len(res)==1:
     print('nan')
   else:
     print(float(res[5]))
     finit=float(res[5])
   
   # Rx background
   proc = subprocess.Popen('grep -A1 \"'+rxbkg+'\" '+filename+' |grep -v \"'+rxbkg+'\"',shell=True,stdout=subprocess.PIPE,bufsize=1, universal_newlines=True)
   output=proc.stdout.read()
   res=output.split(" ")
   if len(res)==1:
     print('nan')
     allres[0,ic,ir]=float('nan')
   else:
     print(float(res[4]))
     allres[0,ic,ir]=float(res[4])-finit
   
   # Domain background
   proc = subprocess.Popen('grep -A1 \"'+dombkg+'\" '+filename+' |grep -v \"'+dombkg+'\"',shell=True,stdout=subprocess.PIPE,bufsize=1, universal_newlines=True)
   output=proc.stdout.read()
   res=output.split(" ")
   if len(res)==1:
     print('nan')
     allres[1,ic,ir]=float('nan')
   else:
     print(float(res[4]))
     allres[1,ic,ir]=float(res[4])-allres[0,ic,ir]
   
   # Domain greens
   proc = subprocess.Popen('grep -A1 \"'+domgrn+'\" '+filename+' |grep -v \"'+domgrn+'\"',shell=True,stdout=subprocess.PIPE,bufsize=1, universal_newlines=True)
   output=proc.stdout.read()
   res=output.split(" ")
   if len(res)==1:
     print('nan')
     allres[2,ic,ir]=float('nan')
   else:
     print(float(res[4]))
     allres[2,ic,ir]=float(res[4])-allres[1,ic,ir]
   
   # Domain background
   proc = subprocess.Popen('grep -A1 \"'+firstmod+'\" '+filename+' |grep -v \"'+firstmod+'\"',shell=True,stdout=subprocess.PIPE,bufsize=1, universal_newlines=True)
   output=proc.stdout.read()
   res=output.split(" ")
   if len(res)==1:
     print('nan')
     allres[3,ic,ir]=float('nan')
   else:
     print(float(res[4]))
     allres[3,ic,ir]=float(res[4])-allres[2,ic,ir]
   
   # Frechet
   proc = subprocess.Popen('grep \"'+frechet+'\" '+filename+' | tail -n1',shell=True,stdout=subprocess.PIPE,bufsize=1, universal_newlines=True)
   output=proc.stdout.read()
   res=output.split(" ")
   if len(res)==1:
     print('nan')
     allres[4,ic,ir]=float('nan')
   else:
     print(float(res[30][:-1]))
     allres[4,ic,ir]=float(res[30][:-1]) 
   
   # Totals
   proc = subprocess.Popen('grep \"'+total+'\" '+filename,shell=True,stdout=subprocess.PIPE,bufsize=1, universal_newlines=True)
   output=proc.stdout.read()
   res=output.split(" ")
   if len(res)==1:
     print('nan')
     allres[5,ic,ir]=float('nan')
     allres[6,ic,ir]=float('nan')
   else:
     print(float(res[7][:-1]))
     print(float(res[4][:-1]))
     allres[5,ic,ir]=float(res[7][:-1])  #total modeling
     allres[6,ic,ir]=float(res[4][:-1])  #total



np.save('temp',allres)

# mean value over runs and CPUs
res=np.nanmean(allres,axis=2)

# pandas data frame and save to csv
resframe=pd.DataFrame(res,index=mybench,columns=cpus)
resframe.to_csv('mean.csv')

# mean value over runs and CPUs
res=np.nanstd(allres,axis=2)

# pandas data frame and save to csv
resframe=pd.DataFrame(res,index=mybench,columns=cpus)
resframe.to_csv('std.csv')

# Write the array to disk
with file('allout.txt', 'w') as outfile:
    # I'm writing a header here just for the sake of readability
    # Any line starting with "#" will be ignored by numpy.loadtxt
    outfile.write('# Array shape: {0}\n'.format(allres.shape))

    # Iterating through a ndimensional array produces slices along
    # the last axis. This is equivalent to data[i,:,:] in this case
    for data_slice in allres:

        # The formatting string indicates that I'm writing out
        # the values in left-justified columns 7 characters in width
        # with 2 decimal places.  
        np.savetxt(outfile, data_slice, fmt='%-7.2f')

        # Writing out a break to indicate different slices...
        outfile.write('# New slice\n')

print('output written in file mean.csv and std.csv')


