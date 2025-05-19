#!/usr/bin/gnuplot -persist

set terminal postscript eps enhanced color

set font "Helvetica,10"
set tics font "Helvetica,18"
set key font "Helvetica,20"

set xlabel "Solved Instances" font "Helvetica,18"
set ylabel "CPU Time [s]" font "Helvetica,18"

eps_file = "results/cactus_all_log.eps"
set output eps_file
csv = "results/time_all_for_cactus.dat"

cactus(method) = sprintf("< echo 0; grep %s, %s | cut -d',' -f 2 | sort -n", method, csv)

set key top left
set style data linespoints
set logscale y

plot [0:340] [:1800] \
cactus("PyBoolNet") title "PyBoolNet" lc rgb "purple",\
cactus("fASP_conj") title "fASP-conj" lc rgb "green",\
cactus("SAF") title "SAF" lc rgb "orange",\
cactus("fASP_src") title "fASP-src" lc rgb "skyblue",\
cactus("SAF_SharpSAT-TD") title "SAF Count." lc rgb "royalblue",\
cactus("Hybrid_BMSA") title "Hybrid Enum." lc rgb "dark-green",\
cactus("AEON") title "AEON" lc rgb "gold",\
cactus("Tseitin_SharpSAT-TD") title "Direct Count." lc rgb "blue",\
cactus("PI_SharpSAT-TD") title "Indirect Count." lc rgb "red",\
cactus("Hybrid_SharpSAT-TD") title "Hybrid Count." lc rgb "black"

set terminal qt
replot
