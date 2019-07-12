import string
import sys
import time
import glob
import subprocess
import numpy as np
import pandas as pd

# labels for the output lines
mybench=['HPL_Tflops','StarDGEMM_Gflops','SingleDGEMM_Gflops','PTRANS_GBs','MPIRandomAccess_GUPs','StarRandomAccess_GUPs','SingleRandomAccess_GUPs','StarSTREAM_Triad','SingleSTREAM_Triad','StarFFT_Gflops','SingleFFT_Gflops','MPIFFT_Gflops']

# find all output files
myfiles=glob.glob('hpccoutf.txt*')
cpus=sorted(set([x.split(".")[2] for x in myfiles]),key=int)
runs=sorted(set([x.split(".")[3] for x in myfiles]),key=int)

# create array for all results
allres=np.zeros([len(mybench),len(cpus),len(runs)],order='F')
print('CPUs',cpus)
print('Runs',runs)
print('Benchmarks',mybench)

# loop over all results and fill in the results data array
for ic, cpu in enumerate(cpus):
  for ir, run in enumerate(runs):
     filename='hpccoutf.txt.'+`cpu`+'.'+`run`
#    perl hpccoutf.pl -w -f hpccoutf.txt.16.1
     proc = subprocess.Popen('perl hpccoutf.pl -a -f '+filename,shell=True,stdout=subprocess.PIPE,bufsize=1, universal_newlines=True)
     output=proc.stdout.read()
     data=output.split("\n")

     for ib, bench in enumerate(mybench):
       #print(ib,ic,ir)
       result=[s for s in data if bench in s]
       #print(result)
       res=result[0].split(":")
       #print(float(res[1]))
       allres[ib,ic,ir]=float(''.join(res[1]))

np.save('temp',allres)

# mean value over runs and CPUs
res=np.mean(allres,axis=2)

# pandas data frame and save to csv
resframe=pd.DataFrame(res,index=mybench,columns=cpus)
resframe.to_csv('mean.csv')

# mean value over runs and CPUs
res=np.std(allres,axis=2)

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



