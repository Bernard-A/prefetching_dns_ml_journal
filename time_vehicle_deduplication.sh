cp Antennas_for_time_final.csv donneesa

# Retirer étiquettes colonnes

awk -v FS="," '{print $1,$2,$3,$4,$5,$6}' donneesa > donneesb

awk -v FS=":" '{print $1,$2,$3,$4,$5,$6}' donneesb > donneesc

awk '{print $3+$2*60+$1*60*60,$4,$5,$6,$7,$8}' donneesc > donneesd

awk '{i++;r[i]=$1;s[i]=$2;t[i]=$3;u[i]=$4;v[i]=$5;w[i]=$6;if (i==10) {for (j=1;j<=10;j++) printf("%d %d %d %d %d %d ",r[j],s[j],t[j],u[j],v[j],w[j]);printf("\n");i=0}}' donneesd > donneesf

## Hourly deduplication

awk '{numtraj+=1;for (i=0;i<1000;i++) {y=rand();x=3600*y;if (i==0) x=0;printf("%d %d ",(numtraj-1)*1000+i,x);for (j=0;j<10;j++) {printf("%d %d %d %d %d %d ",$(j*6+1)+x,$(j*6+2),$(j*6+3),$(j*6+4),$(j*6+5),$(j*6+6))};printf("\n");}}' donneesf > donneesg

## Trajectory re-split
echo "NumTraj RandValue Time Antenna0 Antenna1 Antenna2 Antenna3 Antenna4" > donneesgSplittedForPython

awk '{for(j=0;j<10;j++){printf("%d %d %d %d %d %d %d %d ",$1,$2,$(j*6+3),$(j*6+4),$(j*6+5),$(j*6+6),$(j*6+7),$(j*6+8));printf("\n");}}' donneesg >> donneesgSplittedForPython

## Daily deduplication

awk '{numtraj+=1;for (i=0;i<1000;i++) {y=rand();x=86400*y;if (i==0) x=0;printf("%d %d ",(numtraj-1)*1000+i,x);for (j=0;j<10;j++) {printf("%d %d %d %d %d %d ",($(j*6+1)+x>24*60*60?$(j*6+1)+x-24*60*60,$(j*6+1)+x),$(j*6+2),$(j*6+3),$(j*6+4),$(j*6+5),$(j*6+6))};printf("\n");}}' donneesf > donneesh

## Trajectory re-split
echo "NumTraj RandValue Time Antenna0 Antenna1 Antenna2 Antenna3 Antenna4" > donneeshSplittedForPython

awk '{for(j=0;j<10;j++){printf("%d %d %d %d %d %d %d %d ",$1,$2,$(j*6+3),$(j*6+4),$(j*6+5),$(j*6+6),$(j*6+7),$(j*6+8));printf("\n");}}' donneesh >> donneeshSplittedForPython
