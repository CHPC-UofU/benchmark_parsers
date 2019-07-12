import string
import sys
import time
import glob
import subprocess
import numpy as np
import pandas as pd

metrics=['Mop/s total','Mop/s/thread']
# find all output files
myfiles=glob.glob('*.out')
cpus=sorted(set([x.split(".")[2] for x in myfiles]),key=int)
runs=sorted(set([x.split(".")[3] for x in myfiles]),key=int)
sizes=sorted(set([x.split(".")[1] for x in myfiles]))
mybench=sorted(set([x.split(".")[0] for x in myfiles]))

# create array for all results
print('CPUs',cpus)
print('Runs',runs)
print('Sizes',sizes)
print('Benchmarks',mybench)

# loop over all results and fill in the results data array
for im, metric in enumerate(metrics):
  # create array for all results
  allres=np.zeros([len(mybench),len(sizes),len(cpus),len(runs)],order='F')
  for ib, bench in enumerate(mybench):
    for iz, size in enumerate(sizes):
      for ic, cpu in enumerate(cpus):
        for ir, run in enumerate(runs):
           filename=bench+'.'+size+'.'+`cpu`+'.'+`run`+'.out'
           print(filename)
           proc = subprocess.Popen('grep \"'+metric+'\" '+filename,shell=True,stdout=subprocess.PIPE,bufsize=1, universal_newlines=True)
           output=proc.stdout.read()
           res=output.split("=")
           print(res,len(res))
           if len(res)==1:
             print('nan')
             allres[ib,iz,ic,ir]=float('nan')
           else:
             print(float(res[1]))
             allres[ib,iz,ic,ir]=float(''.join(res[1]))

  metric=metric.replace(' ','_').replace('/','')
  np.save('temp'+metric,allres)

  # loop over sizes
  for iz, size in enumerate(sizes):

    # extract subset of data

    # mean value over runs and CPUs
    res=np.nanmean(allres[:,iz,:,:],axis=2)
   
    # pandas data frame and save to csv
    resframe=pd.DataFrame(res,index=mybench,columns=cpus)
    resframe.to_csv(size+metric+'_mean.csv')
   
    # mean value over runs and CPUs
    res=np.nanstd(allres[:,iz,:,:],axis=2)
   
    # pandas data frame and save to csv
    resframe=pd.DataFrame(res,index=mybench,columns=cpus)
    resframe.to_csv(size+metric+'_std.csv')

  # Write the array to disk
  with file(metric+'_allout.txt', 'w') as outfile:
     # I'm writing a header here just for the sake of readability
     # Any line starting with "#" will be ignored by numpy.loadtxt
     outfile.write('# Array shape: {0}\n'.format(allres.shape))

     # Iterating through a ndimensional array produces slices along
     # the last axis. This is equivalent to data[i,:,:] in this case
     ib=0
     iz=0
     for data_slice in allres:
        for subslice in data_slice:
          # Writing out a break to indicate different slices...
          outfile.write('Benchmark '+mybench[ib]+' size '+sizes[iz]+' \n')
          # The formatting string indicates that I'm writing out
          # the values in left-justified columns 7 characters in width
          # with 2 decimal places.  
          np.savetxt(outfile, subslice, fmt='%-7.2f')
          iz=iz+1
        ib=ib+1
        iz=0
  del allres

print('output written in file mean.csv and std.csv')



