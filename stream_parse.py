import string
import sys
import time
import glob
import subprocess
import numpy as np
import pandas as pd

# find all output files
myfiles=glob.glob('stream.out.*')
cpus=sorted(set([x.split(".")[3] for x in myfiles]),key=int)
runs=sorted(set([x.split(".")[4] for x in myfiles]),key=int)
sizes=sorted(set([x.split(".")[2] for x in myfiles]))
metrics=('Copy','Scale','Add','Triad')

# create array for all results
print('CPUs',cpus)
print('Runs',runs)
print('Sizes',sizes)

# loop over all results and fill in the results data array
for im, metric in enumerate(metrics):
  # create array for all results
  allres=np.zeros([len(sizes),len(cpus),len(runs)],order='F')
  for iz, size in enumerate(sizes):
    for ic, cpu in enumerate(cpus):
      for ir, run in enumerate(runs):
         filename='stream.out.'+size+'.'+`cpu`+'.'+`run`
         print(filename)
         proc = subprocess.Popen('grep \"'+metric+'\" '+filename,shell=True,stdout=subprocess.PIPE,bufsize=1, universal_newlines=True)
         output=proc.stdout.read()
         res=output.split()
         print(res,len(res))
         if len(res)==1:
           print('nan')
           allres[iz,ic,ir]=float('nan')
         else:
           print(float(res[1]))
           allres[iz,ic,ir]=float(''.join(res[1]))

  metric=metric.replace(' ','_').replace('/','')
  np.save('temp'+metric,allres)

  # loop over sizes
  for iz, size in enumerate(sizes):

    # extract subset of data

    # mean value over runs and CPUs
    res=np.nanmean(allres[iz,:,:],axis=1)
    # mean value over runs and CPUs
    std=np.nanstd(allres[iz,:,:],axis=1)
    meanstd=np.stack((res,std),axis=1)
   
    # pandas data frame and save to csv
    collab=('mean','std')
    resframe=pd.DataFrame(meanstd,index=cpus,columns=collab)
    resframe.name=size
    resframe.to_csv(size+metric+'result.csv',index_label=size)


  # Write the array to disk
  with file(metric+'_allout.txt', 'w') as outfile:
     # I'm writing a header here just for the sake of readability
     # Any line starting with "#" will be ignored by numpy.loadtxt
     outfile.write('# Array shape: {0}\n'.format(allres.shape))

     # Iterating through a ndimensional array produces slices along
     # the last axis. This is equivalent to data[i,:,:] in this case
     iz=0
     ib=0
     for data_slice in allres:
        for subslice in data_slice:
          # Writing out a break to indicate different slices...
          outfile.write('cpu'+cpus[iz]+'size '+sizes[ib]+' \n')
          # The formatting string indicates that I'm writing out
          # the values in left-justified columns 7 characters in width
          # with 2 decimal places.  
          np.savetxt(outfile, subslice, fmt='%-7.2f')
          iz=iz+1
          print(iz,subslice)
        iz=0
        ib=ib+1
  del allres

print('output written in file result.csv')



