#!/usr/bin/gnuplot -persist

set terminal postscript eps enhanced color

set font "Helvetica,10"
set tics font "Helvetica,18"
set key font "Helvetica,26"

set xlabel "Solved Instances" font "Helvetica,18"
set ylabel "CPU Time [s]" font "Helvetica,18"

eps_file = "results/cactus_random_log.eps"
set output eps_file
csv = "results/time_pseudo_random_for_cactus.dat"

cactus(method) = sprintf("< echo 0; grep %s, %s | cut -d',' -f 2 | sort -n", method, csv)

set key bottom right
set style data linespoints
set logscale y

plot [0:90] [:1800] \
cactus("PyBoolNet") title "PyBoolNet" lc rgb "purple",\
cactus("SAF") title "SAF" lc rgb "orange",\
cactus("SAF_SharpSAT-TD") title "SAF Count." lc rgb "royalblue",\
cactus("AEON") title "AEON" lc rgb "gold",\
cactus("Hybrid_BMSA") title "Hybrid Enum." lc rgb "dark-green",\
cactus("fASP_conj") title "fASP-conj" lc rgb "green",\
cactus("fASP_src") title "fASP-src" lc rgb "skyblue" pt 7,\
cactus("Tseitin_SharpSAT-TD") title "Direct Count." lc rgb "blue" pt 6,\
cactus("Hybrid_SharpSAT-TD") title "Hybrid Count." lc rgb "black" pt 9,\
cactus("PI_SharpSAT-TD") title "Indirect Count." lc rgb "red" pt 8

set terminal qt
replot
