# Work on a copy of input data
if [ "x$1" == "x" ] || [ "x$1" == "x-h" ];
then
	echo "Usage time_vehicle_deduplication.sh inputfile"
	echo "Output to inputfile_hourly_split and inputfile_daily_split"
else

	cp $1 donneesa
	
	
	
	# Cleans input data
	echo "Cleaning data"
	
	awk -v FS="," '{print $1,$2,$3,$4,$5,$6}' donneesa > donneesb
	
	awk -v FS=":" '{print $1,$2,$3,$4,$5,$6}' donneesb > donneesc
	
	# Changes time in seconds
	
	awk '{print $3+$2*60+$1*60*60,$4,$5,$6,$7,$8}' donneesc > donneesd
	
	# Puts all points on a single line
	
	awk '{i++;r[i]=$1;s[i]=$2;t[i]=$3;u[i]=$4;v[i]=$5;w[i]=$6;if (i==10) {for (j=1;j<=10;j++) printf("%d %d %d %d %d %d ",r[j],s[j],t[j],u[j],v[j],w[j]);printf("\n");i=0}}' donneesd > donneese
	
	# Duplicates the trajectory on a hourly basis (scenario 1)
	echo "Generating data for scenario 1"
	
	## Duplication
	awk '{numtraj+=1;for (i=0;i<1000;i++) {y=rand();x=3600*y;if (i==0) x=0;printf("%d %d ",(numtraj-1)*1000+i,x);for (j=0;j<10;j++) {printf("%d %d %d %d %d %d ",$(j*6+1)+x,$(j*6+2),$(j*6+3),$(j*6+4),$(j*6+5),$(j*6+6))};printf("\n");}}' donneese > donneesf
	
	## Adds label for pandas dataframe (python script)
	echo "NumTraj RandValue Time Antenna0 Antenna1 Antenna2 Antenna3 Antenna4" > donneesfSplittedForPython
	
	## Splits trajectories back
	awk '{for(j=0;j<10;j++){printf("%d %d %d %d %d %d %d %d ",$1,$2,$(j*6+3),$(j*6+4),$(j*6+5),$(j*6+6),$(j*6+7),$(j*6+8));printf("\n");}}' donneesf >> donneesfSplittedForPython
	
	# Duplicates the trajectory on a daily basis (scenario 2)
	echo "Generating data for scenario 2"
	## Duplication
	awk '{numtraj+=1;for (i=0;i<1000;i++) {y=rand();x=24*60*60*y;if (i==0) x=0;printf("%d %d ",(numtraj-1)*1000+i,x);for (j=0;j<10;j++) {if (j==0) over=0; if (j==0 && $1+x>25*60*60) over=1; printf("%d %d %d %d %d %d ",$(j*6+1)+x-(over*24*60*60),$(j*6+2),$(j*6+3),$(j*6+4),$(j*6+5),$(j*6+6))};printf("\n");}}' donneese > donneesg
	
	## Adds label for pandas dataframe (python script)
	echo "NumTraj RandValue Time Antenna0 Antenna1 Antenna2 Antenna3 Antenna4" > donneesgSplittedForPython
	
	## Splits trajectories back
	awk '{for(j=0;j<10;j++){printf("%d %d %d %d %d %d %d %d ",$1,$2,($(j*6+3)>0?$(j*6+3):$(j*6+3)+24*60*60),$(j*6+4),$(j*6+5),$(j*6+6),$(j*6+7),$(j*6+8));printf("\n");}}' donneesg >> donneesgSplittedForPython
	
	# Write to correct folder
	echo "Writing output to correct file"
	cp donneesfSplittedForPython $1_hourly_split
	cp donneesgSplittedForPython $1_daily_split
	
	# Cleaning temporary files
	echo "Removing temporary files"
	rm donneesa donneesb donneesc donneesd donneese donneesf donneesg donneesfSplittedForPython donneesgSplittedForPython
fi
