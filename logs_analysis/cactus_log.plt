#!/usr/bin/gnuplot -persist

set terminal postscript eps enhanced color

set font "Helvetica,10"
set tics font "Helvetica,18"
set key font "Helvetica,22"

set xlabel "Solved Instances" font "Helvetica,18"
set ylabel "CPU Time [s]" font "Helvetica,18"

eps_file = "results/cactus_log.eps"
set output eps_file
csv = "results/time_for_cactus.dat"

cactus(method) = sprintf("< echo 0; grep %s, %s | cut -d',' -f 2 | sort -n", method, csv)

set key top left
set style data linespoints
set logscale y

set arrow from 230,0.01 to 230,1800 nohead lc rgb "black" dashtype 2

plot [0:240] [:1800] \
cactus("PyBoolNet") title "PyBoolNet" lc rgb "purple",\
cactus("fASP_conj") title "fASP-conj" lc rgb "green",\
cactus("fASP_src") title "fASP-src" lc rgb "skyblue",\
cactus("Hybrid_BMSA") title "Hybrid Enum." lc rgb "dark-green",\
cactus("SAF") title "SAF" lc rgb "orange",\
cactus("AEON") title "AEON" lc rgb "gold",\
cactus("SAF_SharpSAT-TD") title "SAF Count." lc rgb "royalblue",\
cactus("PI_SharpSAT-TD") title "Indirect Count." lc rgb "red",\
cactus("Hybrid_SharpSAT-TD") title "Hybrid Count." lc rgb "black",\
cactus("Tseitin_SharpSAT-TD") title "Direct Count." lc rgb "blue"

set terminal qt
replot
