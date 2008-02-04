#include "glt_rgb.h"

/*! \file
    \ingroup GLT
    
    $Id: rgb.cpp,v 1.5 2002/10/09 15:09:38 nigels Exp $
    
    $Log: rgb.cpp,v $
    Revision 1.5  2002/10/09 15:09:38  nigels
    Added RCS Id and Log tags


*/

const GltColor aliceBlue           (0.94118,0.97255,1.00000);
const GltColor antiqueWhite        (0.98039,0.92157,0.84314);
const GltColor antiqueWhite1       (1.00000,0.93725,0.85882);
const GltColor antiqueWhite2       (0.93333,0.87451,0.80000);
const GltColor antiqueWhite3       (0.80392,0.75294,0.69020);
const GltColor antiqueWhite4       (0.54510,0.51373,0.47059);
const GltColor aquamarine          (0.49804,1.00000,0.83137);
const GltColor aquamarine1         (0.49804,1.00000,0.83137);
const GltColor aquamarine2         (0.46275,0.93333,0.77647);
const GltColor aquamarine3         (0.40000,0.80392,0.66667);
const GltColor aquamarine4         (0.27059,0.54510,0.45490);
const GltColor azure               (0.94118,1.00000,1.00000);
const GltColor azure1              (0.94118,1.00000,1.00000);
const GltColor azure2              (0.87843,0.93333,0.93333);
const GltColor azure3              (0.75686,0.80392,0.80392);
const GltColor azure4              (0.51373,0.54510,0.54510);
const GltColor beige               (0.96078,0.96078,0.86275);
const GltColor bisque              (1.00000,0.89412,0.76863);
const GltColor bisque1             (1.00000,0.89412,0.76863);
const GltColor bisque2             (0.93333,0.83529,0.71765);
const GltColor bisque3             (0.80392,0.71765,0.61961);
const GltColor bisque4             (0.54510,0.49020,0.41961);
const GltColor black               (0.00000,0.00000,0.00000);
const GltColor blanchedAlmond      (1.00000,0.92157,0.80392);
const GltColor blue                (0.00000,0.00000,1.00000);
const GltColor blue1               (0.00000,0.00000,1.00000);
const GltColor blue2               (0.00000,0.00000,0.93333);
const GltColor blue3               (0.00000,0.00000,0.80392);
const GltColor blue4               (0.00000,0.00000,0.54510);
const GltColor blueViolet          (0.54118,0.16863,0.88627);
const GltColor brown               (0.64706,0.16471,0.16471);
const GltColor brown1              (1.00000,0.25098,0.25098);
const GltColor brown2              (0.93333,0.23137,0.23137);
const GltColor brown3              (0.80392,0.20000,0.20000);
const GltColor brown4              (0.54510,0.13725,0.13725);
const GltColor burlywood           (0.87059,0.72157,0.52941);
const GltColor burlywood1          (1.00000,0.82745,0.60784);
const GltColor burlywood2          (0.93333,0.77255,0.56863);
const GltColor burlywood3          (0.80392,0.66667,0.49020);
const GltColor burlywood4          (0.54510,0.45098,0.33333);
const GltColor cadetBlue           (0.37255,0.61961,0.62745);
const GltColor cadetBlue1          (0.59608,0.96078,1.00000);
const GltColor cadetBlue2          (0.55686,0.89804,0.93333);
const GltColor cadetBlue3          (0.47843,0.77255,0.80392);
const GltColor cadetBlue4          (0.32549,0.52549,0.54510);
const GltColor chartreuse          (0.49804,1.00000,0.00000);
const GltColor chartreuse1         (0.49804,1.00000,0.00000);
const GltColor chartreuse2         (0.46275,0.93333,0.00000);
const GltColor chartreuse3         (0.40000,0.80392,0.00000);
const GltColor chartreuse4         (0.27059,0.54510,0.00000);
const GltColor chocolate           (0.82353,0.41176,0.11765);
const GltColor chocolate1          (1.00000,0.49804,0.14118);
const GltColor chocolate2          (0.93333,0.46275,0.12941);
const GltColor chocolate3          (0.80392,0.40000,0.11373);
const GltColor chocolate4          (0.54510,0.27059,0.07451);
const GltColor coral               (1.00000,0.49804,0.31373);
const GltColor coral1              (1.00000,0.44706,0.33725);
const GltColor coral2              (0.93333,0.41569,0.31373);
const GltColor coral3              (0.80392,0.35686,0.27059);
const GltColor coral4              (0.54510,0.24314,0.18431);
const GltColor cornflowerBlue      (0.39216,0.58431,0.92941);
const GltColor cornsilk            (1.00000,0.97255,0.86275);
const GltColor cornsilk1           (1.00000,0.97255,0.86275);
const GltColor cornsilk2           (0.93333,0.90980,0.80392);
const GltColor cornsilk3           (0.80392,0.78431,0.69412);
const GltColor cornsilk4           (0.54510,0.53333,0.47059);
const GltColor cyan                (0.00000,1.00000,1.00000);
const GltColor cyan1               (0.00000,1.00000,1.00000);
const GltColor cyan2               (0.00000,0.93333,0.93333);
const GltColor cyan3               (0.00000,0.80392,0.80392);
const GltColor cyan4               (0.00000,0.54510,0.54510);
const GltColor darkBlue            (0.00000,0.00000,0.54510);
const GltColor darkCyan            (0.00000,0.54510,0.54510);
const GltColor darkGoldenrod       (0.72157,0.52549,0.04314);
const GltColor darkGoldenrod1      (1.00000,0.72549,0.05882);
const GltColor darkGoldenrod2      (0.93333,0.67843,0.05490);
const GltColor darkGoldenrod3      (0.80392,0.58431,0.04706);
const GltColor darkGoldenrod4      (0.54510,0.39608,0.03137);
const GltColor darkGray            (0.66275,0.66275,0.66275);
const GltColor darkGreen           (0.00000,0.39216,0.00000);
const GltColor darkGrey            (0.66275,0.66275,0.66275);
const GltColor darkKhaki           (0.74118,0.71765,0.41961);
const GltColor darkMagenta         (0.54510,0.00000,0.54510);
const GltColor darkOliveGreen      (0.33333,0.41961,0.18431);
const GltColor darkOliveGreen1     (0.79216,1.00000,0.43922);
const GltColor darkOliveGreen2     (0.73725,0.93333,0.40784);
const GltColor darkOliveGreen3     (0.63529,0.80392,0.35294);
const GltColor darkOliveGreen4     (0.43137,0.54510,0.23922);
const GltColor darkOrange          (1.00000,0.54902,0.00000);
const GltColor darkOrange1         (1.00000,0.49804,0.00000);
const GltColor darkOrange2         (0.93333,0.46275,0.00000);
const GltColor darkOrange3         (0.80392,0.40000,0.00000);
const GltColor darkOrange4         (0.54510,0.27059,0.00000);
const GltColor darkOrchid          (0.60000,0.19608,0.80000);
const GltColor darkOrchid1         (0.74902,0.24314,1.00000);
const GltColor darkOrchid2         (0.69804,0.22745,0.93333);
const GltColor darkOrchid3         (0.60392,0.19608,0.80392);
const GltColor darkOrchid4         (0.40784,0.13333,0.54510);
const GltColor darkRed             (0.54510,0.00000,0.00000);
const GltColor darkSalmon          (0.91373,0.58824,0.47843);
const GltColor darkSeaGreen        (0.56078,0.73725,0.56078);
const GltColor darkSeaGreen1       (0.75686,1.00000,0.75686);
const GltColor darkSeaGreen2       (0.70588,0.93333,0.70588);
const GltColor darkSeaGreen3       (0.60784,0.80392,0.60784);
const GltColor darkSeaGreen4       (0.41176,0.54510,0.41176);
const GltColor darkSlateBlue       (0.28235,0.23922,0.54510);
const GltColor darkSlateGray       (0.18431,0.30980,0.30980);
const GltColor darkSlateGray1      (0.59216,1.00000,1.00000);
const GltColor darkSlateGray2      (0.55294,0.93333,0.93333);
const GltColor darkSlateGray3      (0.47451,0.80392,0.80392);
const GltColor darkSlateGray4      (0.32157,0.54510,0.54510);
const GltColor darkSlateGrey       (0.18431,0.30980,0.30980);
const GltColor darkTurquoise       (0.00000,0.80784,0.81961);
const GltColor darkViolet          (0.58039,0.00000,0.82745);
const GltColor deepPink            (1.00000,0.07843,0.57647);
const GltColor deepPink1           (1.00000,0.07843,0.57647);
const GltColor deepPink2           (0.93333,0.07059,0.53725);
const GltColor deepPink3           (0.80392,0.06275,0.46275);
const GltColor deepPink4           (0.54510,0.03922,0.31373);
const GltColor deepSkyBlue         (0.00000,0.74902,1.00000);
const GltColor deepSkyBlue1        (0.00000,0.74902,1.00000);
const GltColor deepSkyBlue2        (0.00000,0.69804,0.93333);
const GltColor deepSkyBlue3        (0.00000,0.60392,0.80392);
const GltColor deepSkyBlue4        (0.00000,0.40784,0.54510);
const GltColor dimGray             (0.41176,0.41176,0.41176);
const GltColor dimGrey             (0.41176,0.41176,0.41176);
const GltColor dodgerBlue          (0.11765,0.56471,1.00000);
const GltColor dodgerBlue1         (0.11765,0.56471,1.00000);
const GltColor dodgerBlue2         (0.10980,0.52549,0.93333);
const GltColor dodgerBlue3         (0.09412,0.45490,0.80392);
const GltColor dodgerBlue4         (0.06275,0.30588,0.54510);
const GltColor firebrick           (0.69804,0.13333,0.13333);
const GltColor firebrick1          (1.00000,0.18824,0.18824);
const GltColor firebrick2          (0.93333,0.17255,0.17255);
const GltColor firebrick3          (0.80392,0.14902,0.14902);
const GltColor firebrick4          (0.54510,0.10196,0.10196);
const GltColor floralWhite         (1.00000,0.98039,0.94118);
const GltColor forestGreen         (0.13333,0.54510,0.13333);
const GltColor gainsboro           (0.86275,0.86275,0.86275);
const GltColor ghostWhite          (0.97255,0.97255,1.00000);
const GltColor gold                (1.00000,0.84314,0.00000);
const GltColor gold1               (1.00000,0.84314,0.00000);
const GltColor gold2               (0.93333,0.78824,0.00000);
const GltColor gold3               (0.80392,0.67843,0.00000);
const GltColor gold4               (0.54510,0.45882,0.00000);
const GltColor goldenrod           (0.85490,0.64706,0.12549);
const GltColor goldenrod1          (1.00000,0.75686,0.14510);
const GltColor goldenrod2          (0.93333,0.70588,0.13333);
const GltColor goldenrod3          (0.80392,0.60784,0.11373);
const GltColor goldenrod4          (0.54510,0.41176,0.07843);
const GltColor gray                (0.74510,0.74510,0.74510);
const GltColor gray0               (0.00000,0.00000,0.00000);
const GltColor gray1               (0.01176,0.01176,0.01176);
const GltColor gray10              (0.10196,0.10196,0.10196);
const GltColor gray100             (1.00000,1.00000,1.00000);
const GltColor gray11              (0.10980,0.10980,0.10980);
const GltColor gray12              (0.12157,0.12157,0.12157);
const GltColor gray13              (0.12941,0.12941,0.12941);
const GltColor gray14              (0.14118,0.14118,0.14118);
const GltColor gray15              (0.14902,0.14902,0.14902);
const GltColor gray16              (0.16078,0.16078,0.16078);
const GltColor gray17              (0.16863,0.16863,0.16863);
const GltColor gray18              (0.18039,0.18039,0.18039);
const GltColor gray19              (0.18824,0.18824,0.18824);
const GltColor gray2               (0.01961,0.01961,0.01961);
const GltColor gray20              (0.20000,0.20000,0.20000);
const GltColor gray21              (0.21176,0.21176,0.21176);
const GltColor gray22              (0.21961,0.21961,0.21961);
const GltColor gray23              (0.23137,0.23137,0.23137);
const GltColor gray24              (0.23922,0.23922,0.23922);
const GltColor gray25              (0.25098,0.25098,0.25098);
const GltColor gray26              (0.25882,0.25882,0.25882);
const GltColor gray27              (0.27059,0.27059,0.27059);
const GltColor gray28              (0.27843,0.27843,0.27843);
const GltColor gray29              (0.29020,0.29020,0.29020);
const GltColor gray3               (0.03137,0.03137,0.03137);
const GltColor gray30              (0.30196,0.30196,0.30196);
const GltColor gray31              (0.30980,0.30980,0.30980);
const GltColor gray32              (0.32157,0.32157,0.32157);
const GltColor gray33              (0.32941,0.32941,0.32941);
const GltColor gray34              (0.34118,0.34118,0.34118);
const GltColor gray35              (0.34902,0.34902,0.34902);
const GltColor gray36              (0.36078,0.36078,0.36078);
const GltColor gray37              (0.36863,0.36863,0.36863);
const GltColor gray38              (0.38039,0.38039,0.38039);
const GltColor gray39              (0.38824,0.38824,0.38824);
const GltColor gray4               (0.03922,0.03922,0.03922);
const GltColor gray40              (0.40000,0.40000,0.40000);
const GltColor gray41              (0.41176,0.41176,0.41176);
const GltColor gray42              (0.41961,0.41961,0.41961);
const GltColor gray43              (0.43137,0.43137,0.43137);
const GltColor gray44              (0.43922,0.43922,0.43922);
const GltColor gray45              (0.45098,0.45098,0.45098);
const GltColor gray46              (0.45882,0.45882,0.45882);
const GltColor gray47              (0.47059,0.47059,0.47059);
const GltColor gray48              (0.47843,0.47843,0.47843);
const GltColor gray49              (0.49020,0.49020,0.49020);
const GltColor gray5               (0.05098,0.05098,0.05098);
const GltColor gray50              (0.49804,0.49804,0.49804);
const GltColor gray51              (0.50980,0.50980,0.50980);
const GltColor gray52              (0.52157,0.52157,0.52157);
const GltColor gray53              (0.52941,0.52941,0.52941);
const GltColor gray54              (0.54118,0.54118,0.54118);
const GltColor gray55              (0.54902,0.54902,0.54902);
const GltColor gray56              (0.56078,0.56078,0.56078);
const GltColor gray57              (0.56863,0.56863,0.56863);
const GltColor gray58              (0.58039,0.58039,0.58039);
const GltColor gray59              (0.58824,0.58824,0.58824);
const GltColor gray6               (0.05882,0.05882,0.05882);
const GltColor gray60              (0.60000,0.60000,0.60000);
const GltColor gray61              (0.61176,0.61176,0.61176);
const GltColor gray62              (0.61961,0.61961,0.61961);
const GltColor gray63              (0.63137,0.63137,0.63137);
const GltColor gray64              (0.63922,0.63922,0.63922);
const GltColor gray65              (0.65098,0.65098,0.65098);
const GltColor gray66              (0.65882,0.65882,0.65882);
const GltColor gray67              (0.67059,0.67059,0.67059);
const GltColor gray68              (0.67843,0.67843,0.67843);
const GltColor gray69              (0.69020,0.69020,0.69020);
const GltColor gray7               (0.07059,0.07059,0.07059);
const GltColor gray70              (0.70196,0.70196,0.70196);
const GltColor gray71              (0.70980,0.70980,0.70980);
const GltColor gray72              (0.72157,0.72157,0.72157);
const GltColor gray73              (0.72941,0.72941,0.72941);
const GltColor gray74              (0.74118,0.74118,0.74118);
const GltColor gray75              (0.74902,0.74902,0.74902);
const GltColor gray76              (0.76078,0.76078,0.76078);
const GltColor gray77              (0.76863,0.76863,0.76863);
const GltColor gray78              (0.78039,0.78039,0.78039);
const GltColor gray79              (0.78824,0.78824,0.78824);
const GltColor gray8               (0.07843,0.07843,0.07843);
const GltColor gray80              (0.80000,0.80000,0.80000);
const GltColor gray81              (0.81176,0.81176,0.81176);
const GltColor gray82              (0.81961,0.81961,0.81961);
const GltColor gray83              (0.83137,0.83137,0.83137);
const GltColor gray84              (0.83922,0.83922,0.83922);
const GltColor gray85              (0.85098,0.85098,0.85098);
const GltColor gray86              (0.85882,0.85882,0.85882);
const GltColor gray87              (0.87059,0.87059,0.87059);
const GltColor gray88              (0.87843,0.87843,0.87843);
const GltColor gray89              (0.89020,0.89020,0.89020);
const GltColor gray9               (0.09020,0.09020,0.09020);
const GltColor gray90              (0.89804,0.89804,0.89804);
const GltColor gray91              (0.90980,0.90980,0.90980);
const GltColor gray92              (0.92157,0.92157,0.92157);
const GltColor gray93              (0.92941,0.92941,0.92941);
const GltColor gray94              (0.94118,0.94118,0.94118);
const GltColor gray95              (0.94902,0.94902,0.94902);
const GltColor gray96              (0.96078,0.96078,0.96078);
const GltColor gray97              (0.96863,0.96863,0.96863);
const GltColor gray98              (0.98039,0.98039,0.98039);
const GltColor gray99              (0.98824,0.98824,0.98824);
const GltColor green               (0.00000,1.00000,0.00000);
const GltColor green1              (0.00000,1.00000,0.00000);
const GltColor green2              (0.00000,0.93333,0.00000);
const GltColor green3              (0.00000,0.80392,0.00000);
const GltColor green4              (0.00000,0.54510,0.00000);
const GltColor greenYellow         (0.67843,1.00000,0.18431);
const GltColor grey                (0.74510,0.74510,0.74510);
const GltColor grey0               (0.00000,0.00000,0.00000);
const GltColor grey1               (0.01176,0.01176,0.01176);
const GltColor grey10              (0.10196,0.10196,0.10196);
const GltColor grey100             (1.00000,1.00000,1.00000);
const GltColor grey11              (0.10980,0.10980,0.10980);
const GltColor grey12              (0.12157,0.12157,0.12157);
const GltColor grey13              (0.12941,0.12941,0.12941);
const GltColor grey14              (0.14118,0.14118,0.14118);
const GltColor grey15              (0.14902,0.14902,0.14902);
const GltColor grey16              (0.16078,0.16078,0.16078);
const GltColor grey17              (0.16863,0.16863,0.16863);
const GltColor grey18              (0.18039,0.18039,0.18039);
const GltColor grey19              (0.18824,0.18824,0.18824);
const GltColor grey2               (0.01961,0.01961,0.01961);
const GltColor grey20              (0.20000,0.20000,0.20000);
const GltColor grey21              (0.21176,0.21176,0.21176);
const GltColor grey22              (0.21961,0.21961,0.21961);
const GltColor grey23              (0.23137,0.23137,0.23137);
const GltColor grey24              (0.23922,0.23922,0.23922);
const GltColor grey25              (0.25098,0.25098,0.25098);
const GltColor grey26              (0.25882,0.25882,0.25882);
const GltColor grey27              (0.27059,0.27059,0.27059);
const GltColor grey28              (0.27843,0.27843,0.27843);
const GltColor grey29              (0.29020,0.29020,0.29020);
const GltColor grey3               (0.03137,0.03137,0.03137);
const GltColor grey30              (0.30196,0.30196,0.30196);
const GltColor grey31              (0.30980,0.30980,0.30980);
const GltColor grey32              (0.32157,0.32157,0.32157);
const GltColor grey33              (0.32941,0.32941,0.32941);
const GltColor grey34              (0.34118,0.34118,0.34118);
const GltColor grey35              (0.34902,0.34902,0.34902);
const GltColor grey36              (0.36078,0.36078,0.36078);
const GltColor grey37              (0.36863,0.36863,0.36863);
const GltColor grey38              (0.38039,0.38039,0.38039);
const GltColor grey39              (0.38824,0.38824,0.38824);
const GltColor grey4               (0.03922,0.03922,0.03922);
const GltColor grey40              (0.40000,0.40000,0.40000);
const GltColor grey41              (0.41176,0.41176,0.41176);
const GltColor grey42              (0.41961,0.41961,0.41961);
const GltColor grey43              (0.43137,0.43137,0.43137);
const GltColor grey44              (0.43922,0.43922,0.43922);
const GltColor grey45              (0.45098,0.45098,0.45098);
const GltColor grey46              (0.45882,0.45882,0.45882);
const GltColor grey47              (0.47059,0.47059,0.47059);
const GltColor grey48              (0.47843,0.47843,0.47843);
const GltColor grey49              (0.49020,0.49020,0.49020);
const GltColor grey5               (0.05098,0.05098,0.05098);
const GltColor grey50              (0.49804,0.49804,0.49804);
const GltColor grey51              (0.50980,0.50980,0.50980);
const GltColor grey52              (0.52157,0.52157,0.52157);
const GltColor grey53              (0.52941,0.52941,0.52941);
const GltColor grey54              (0.54118,0.54118,0.54118);
const GltColor grey55              (0.54902,0.54902,0.54902);
const GltColor grey56              (0.56078,0.56078,0.56078);
const GltColor grey57              (0.56863,0.56863,0.56863);
const GltColor grey58              (0.58039,0.58039,0.58039);
const GltColor grey59              (0.58824,0.58824,0.58824);
const GltColor grey6               (0.05882,0.05882,0.05882);
const GltColor grey60              (0.60000,0.60000,0.60000);
const GltColor grey61              (0.61176,0.61176,0.61176);
const GltColor grey62              (0.61961,0.61961,0.61961);
const GltColor grey63              (0.63137,0.63137,0.63137);
const GltColor grey64              (0.63922,0.63922,0.63922);
const GltColor grey65              (0.65098,0.65098,0.65098);
const GltColor grey66              (0.65882,0.65882,0.65882);
const GltColor grey67              (0.67059,0.67059,0.67059);
const GltColor grey68              (0.67843,0.67843,0.67843);
const GltColor grey69              (0.69020,0.69020,0.69020);
const GltColor grey7               (0.07059,0.07059,0.07059);
const GltColor grey70              (0.70196,0.70196,0.70196);
const GltColor grey71              (0.70980,0.70980,0.70980);
const GltColor grey72              (0.72157,0.72157,0.72157);
const GltColor grey73              (0.72941,0.72941,0.72941);
const GltColor grey74              (0.74118,0.74118,0.74118);
const GltColor grey75              (0.74902,0.74902,0.74902);
const GltColor grey76              (0.76078,0.76078,0.76078);
const GltColor grey77              (0.76863,0.76863,0.76863);
const GltColor grey78              (0.78039,0.78039,0.78039);
const GltColor grey79              (0.78824,0.78824,0.78824);
const GltColor grey8               (0.07843,0.07843,0.07843);
const GltColor grey80              (0.80000,0.80000,0.80000);
const GltColor grey81              (0.81176,0.81176,0.81176);
const GltColor grey82              (0.81961,0.81961,0.81961);
const GltColor grey83              (0.83137,0.83137,0.83137);
const GltColor grey84              (0.83922,0.83922,0.83922);
const GltColor grey85              (0.85098,0.85098,0.85098);
const GltColor grey86              (0.85882,0.85882,0.85882);
const GltColor grey87              (0.87059,0.87059,0.87059);
const GltColor grey88              (0.87843,0.87843,0.87843);
const GltColor grey89              (0.89020,0.89020,0.89020);
const GltColor grey9               (0.09020,0.09020,0.09020);
const GltColor grey90              (0.89804,0.89804,0.89804);
const GltColor grey91              (0.90980,0.90980,0.90980);
const GltColor grey92              (0.92157,0.92157,0.92157);
const GltColor grey93              (0.92941,0.92941,0.92941);
const GltColor grey94              (0.94118,0.94118,0.94118);
const GltColor grey95              (0.94902,0.94902,0.94902);
const GltColor grey96              (0.96078,0.96078,0.96078);
const GltColor grey97              (0.96863,0.96863,0.96863);
const GltColor grey98              (0.98039,0.98039,0.98039);
const GltColor grey99              (0.98824,0.98824,0.98824);
const GltColor honeydew            (0.94118,1.00000,0.94118);
const GltColor honeydew1           (0.94118,1.00000,0.94118);
const GltColor honeydew2           (0.87843,0.93333,0.87843);
const GltColor honeydew3           (0.75686,0.80392,0.75686);
const GltColor honeydew4           (0.51373,0.54510,0.51373);
const GltColor hotPink             (1.00000,0.41176,0.70588);
const GltColor hotPink1            (1.00000,0.43137,0.70588);
const GltColor hotPink2            (0.93333,0.41569,0.65490);
const GltColor hotPink3            (0.80392,0.37647,0.56471);
const GltColor hotPink4            (0.54510,0.22745,0.38431);
const GltColor indianRed           (0.80392,0.36078,0.36078);
const GltColor indianRed1          (1.00000,0.41569,0.41569);
const GltColor indianRed2          (0.93333,0.38824,0.38824);
const GltColor indianRed3          (0.80392,0.33333,0.33333);
const GltColor indianRed4          (0.54510,0.22745,0.22745);
const GltColor ivory               (1.00000,1.00000,0.94118);
const GltColor ivory1              (1.00000,1.00000,0.94118);
const GltColor ivory2              (0.93333,0.93333,0.87843);
const GltColor ivory3              (0.80392,0.80392,0.75686);
const GltColor ivory4              (0.54510,0.54510,0.51373);
const GltColor khaki               (0.94118,0.90196,0.54902);
const GltColor khaki1              (1.00000,0.96471,0.56078);
const GltColor khaki2              (0.93333,0.90196,0.52157);
const GltColor khaki3              (0.80392,0.77647,0.45098);
const GltColor khaki4              (0.54510,0.52549,0.30588);
const GltColor lavender            (0.90196,0.90196,0.98039);
const GltColor lavenderBlush       (1.00000,0.94118,0.96078);
const GltColor lavenderBlush1      (1.00000,0.94118,0.96078);
const GltColor lavenderBlush2      (0.93333,0.87843,0.89804);
const GltColor lavenderBlush3      (0.80392,0.75686,0.77255);
const GltColor lavenderBlush4      (0.54510,0.51373,0.52549);
const GltColor lawnGreen           (0.48627,0.98824,0.00000);
const GltColor lemonChiffon        (1.00000,0.98039,0.80392);
const GltColor lemonChiffon1       (1.00000,0.98039,0.80392);
const GltColor lemonChiffon2       (0.93333,0.91373,0.74902);
const GltColor lemonChiffon3       (0.80392,0.78824,0.64706);
const GltColor lemonChiffon4       (0.54510,0.53725,0.43922);
const GltColor lightBlue           (0.67843,0.84706,0.90196);
const GltColor lightBlue1          (0.74902,0.93725,1.00000);
const GltColor lightBlue2          (0.69804,0.87451,0.93333);
const GltColor lightBlue3          (0.60392,0.75294,0.80392);
const GltColor lightBlue4          (0.40784,0.51373,0.54510);
const GltColor lightCoral          (0.94118,0.50196,0.50196);
const GltColor lightCyan           (0.87843,1.00000,1.00000);
const GltColor lightCyan1          (0.87843,1.00000,1.00000);
const GltColor lightCyan2          (0.81961,0.93333,0.93333);
const GltColor lightCyan3          (0.70588,0.80392,0.80392);
const GltColor lightCyan4          (0.47843,0.54510,0.54510);
const GltColor lightGoldenrod      (0.93333,0.86667,0.50980);
const GltColor lightGoldenrod1     (1.00000,0.92549,0.54510);
const GltColor lightGoldenrod2     (0.93333,0.86275,0.50980);
const GltColor lightGoldenrod3     (0.80392,0.74510,0.43922);
const GltColor lightGoldenrod4     (0.54510,0.50588,0.29804);
const GltColor lightGoldenrodYellow(0.98039,0.98039,0.82353);
const GltColor lightGray           (0.82745,0.82745,0.82745);
const GltColor lightGreen          (0.56471,0.93333,0.56471);
const GltColor lightGrey           (0.82745,0.82745,0.82745);
const GltColor lightPink           (1.00000,0.71373,0.75686);
const GltColor lightPink1          (1.00000,0.68235,0.72549);
const GltColor lightPink2          (0.93333,0.63529,0.67843);
const GltColor lightPink3          (0.80392,0.54902,0.58431);
const GltColor lightPink4          (0.54510,0.37255,0.39608);
const GltColor lightSalmon         (1.00000,0.62745,0.47843);
const GltColor lightSalmon1        (1.00000,0.62745,0.47843);
const GltColor lightSalmon2        (0.93333,0.58431,0.44706);
const GltColor lightSalmon3        (0.80392,0.50588,0.38431);
const GltColor lightSalmon4        (0.54510,0.34118,0.25882);
const GltColor lightSeaGreen       (0.12549,0.69804,0.66667);
const GltColor lightSkyBlue        (0.52941,0.80784,0.98039);
const GltColor lightSkyBlue1       (0.69020,0.88627,1.00000);
const GltColor lightSkyBlue2       (0.64314,0.82745,0.93333);
const GltColor lightSkyBlue3       (0.55294,0.71373,0.80392);
const GltColor lightSkyBlue4       (0.37647,0.48235,0.54510);
const GltColor lightSlateBlue      (0.51765,0.43922,1.00000);
const GltColor lightSlateGray      (0.46667,0.53333,0.60000);
const GltColor lightSlateGrey      (0.46667,0.53333,0.60000);
const GltColor lightSteelBlue      (0.69020,0.76863,0.87059);
const GltColor lightSteelBlue1     (0.79216,0.88235,1.00000);
const GltColor lightSteelBlue2     (0.73725,0.82353,0.93333);
const GltColor lightSteelBlue3     (0.63529,0.70980,0.80392);
const GltColor lightSteelBlue4     (0.43137,0.48235,0.54510);
const GltColor lightYellow         (1.00000,1.00000,0.87843);
const GltColor lightYellow1        (1.00000,1.00000,0.87843);
const GltColor lightYellow2        (0.93333,0.93333,0.81961);
const GltColor lightYellow3        (0.80392,0.80392,0.70588);
const GltColor lightYellow4        (0.54510,0.54510,0.47843);
const GltColor limeGreen           (0.19608,0.80392,0.19608);
const GltColor linen               (0.98039,0.94118,0.90196);
const GltColor magenta             (1.00000,0.00000,1.00000);
const GltColor magenta1            (1.00000,0.00000,1.00000);
const GltColor magenta2            (0.93333,0.00000,0.93333);
const GltColor magenta3            (0.80392,0.00000,0.80392);
const GltColor magenta4            (0.54510,0.00000,0.54510);
const GltColor maroon              (0.69020,0.18824,0.37647);
const GltColor maroon1             (1.00000,0.20392,0.70196);
const GltColor maroon2             (0.93333,0.18824,0.65490);
const GltColor maroon3             (0.80392,0.16078,0.56471);
const GltColor maroon4             (0.54510,0.10980,0.38431);
const GltColor mediumAquamarine    (0.40000,0.80392,0.66667);
const GltColor mediumBlue          (0.00000,0.00000,0.80392);
const GltColor mediumOrchid        (0.72941,0.33333,0.82745);
const GltColor mediumOrchid1       (0.87843,0.40000,1.00000);
const GltColor mediumOrchid2       (0.81961,0.37255,0.93333);
const GltColor mediumOrchid3       (0.70588,0.32157,0.80392);
const GltColor mediumOrchid4       (0.47843,0.21569,0.54510);
const GltColor mediumPurple        (0.57647,0.43922,0.85882);
const GltColor mediumPurple1       (0.67059,0.50980,1.00000);
const GltColor mediumPurple2       (0.62353,0.47451,0.93333);
const GltColor mediumPurple3       (0.53725,0.40784,0.80392);
const GltColor mediumPurple4       (0.36471,0.27843,0.54510);
const GltColor mediumSeaGreen      (0.23529,0.70196,0.44314);
const GltColor mediumSlateBlue     (0.48235,0.40784,0.93333);
const GltColor mediumSpringGreen   (0.00000,0.98039,0.60392);
const GltColor mediumTurquoise     (0.28235,0.81961,0.80000);
const GltColor mediumVioletRed     (0.78039,0.08235,0.52157);
const GltColor midnightBlue        (0.09804,0.09804,0.43922);
const GltColor mintCream           (0.96078,1.00000,0.98039);
const GltColor mistyRose           (1.00000,0.89412,0.88235);
const GltColor mistyRose1          (1.00000,0.89412,0.88235);
const GltColor mistyRose2          (0.93333,0.83529,0.82353);
const GltColor mistyRose3          (0.80392,0.71765,0.70980);
const GltColor mistyRose4          (0.54510,0.49020,0.48235);
const GltColor moccasin            (1.00000,0.89412,0.70980);
const GltColor navajoWhite         (1.00000,0.87059,0.67843);
const GltColor navajoWhite1        (1.00000,0.87059,0.67843);
const GltColor navajoWhite2        (0.93333,0.81176,0.63137);
const GltColor navajoWhite3        (0.80392,0.70196,0.54510);
const GltColor navajoWhite4        (0.54510,0.47451,0.36863);
const GltColor navy                (0.00000,0.00000,0.50196);
const GltColor navyBlue            (0.00000,0.00000,0.50196);
const GltColor oldLace             (0.99216,0.96078,0.90196);
const GltColor oliveDrab           (0.41961,0.55686,0.13725);
const GltColor oliveDrab1          (0.75294,1.00000,0.24314);
const GltColor oliveDrab2          (0.70196,0.93333,0.22745);
const GltColor oliveDrab3          (0.60392,0.80392,0.19608);
const GltColor oliveDrab4          (0.41176,0.54510,0.13333);
const GltColor orange              (1.00000,0.64706,0.00000);
const GltColor orange1             (1.00000,0.64706,0.00000);
const GltColor orange2             (0.93333,0.60392,0.00000);
const GltColor orange3             (0.80392,0.52157,0.00000);
const GltColor orange4             (0.54510,0.35294,0.00000);
const GltColor orangeRed           (1.00000,0.27059,0.00000);
const GltColor orangeRed1          (1.00000,0.27059,0.00000);
const GltColor orangeRed2          (0.93333,0.25098,0.00000);
const GltColor orangeRed3          (0.80392,0.21569,0.00000);
const GltColor orangeRed4          (0.54510,0.14510,0.00000);
const GltColor orchid              (0.85490,0.43922,0.83922);
const GltColor orchid1             (1.00000,0.51373,0.98039);
const GltColor orchid2             (0.93333,0.47843,0.91373);
const GltColor orchid3             (0.80392,0.41176,0.78824);
const GltColor orchid4             (0.54510,0.27843,0.53725);
const GltColor paleGoldenrod       (0.93333,0.90980,0.66667);
const GltColor paleGreen           (0.59608,0.98431,0.59608);
const GltColor paleGreen1          (0.60392,1.00000,0.60392);
const GltColor paleGreen2          (0.56471,0.93333,0.56471);
const GltColor paleGreen3          (0.48627,0.80392,0.48627);
const GltColor paleGreen4          (0.32941,0.54510,0.32941);
const GltColor paleTurquoise       (0.68627,0.93333,0.93333);
const GltColor paleTurquoise1      (0.73333,1.00000,1.00000);
const GltColor paleTurquoise2      (0.68235,0.93333,0.93333);
const GltColor paleTurquoise3      (0.58824,0.80392,0.80392);
const GltColor paleTurquoise4      (0.40000,0.54510,0.54510);
const GltColor paleVioletRed       (0.85882,0.43922,0.57647);
const GltColor paleVioletRed1      (1.00000,0.50980,0.67059);
const GltColor paleVioletRed2      (0.93333,0.47451,0.62353);
const GltColor paleVioletRed3      (0.80392,0.40784,0.53725);
const GltColor paleVioletRed4      (0.54510,0.27843,0.36471);
const GltColor papayaWhip          (1.00000,0.93725,0.83529);
const GltColor peachPuff           (1.00000,0.85490,0.72549);
const GltColor peachPuff1          (1.00000,0.85490,0.72549);
const GltColor peachPuff2          (0.93333,0.79608,0.67843);
const GltColor peachPuff3          (0.80392,0.68627,0.58431);
const GltColor peachPuff4          (0.54510,0.46667,0.39608);
const GltColor peru                (0.80392,0.52157,0.24706);
const GltColor pink                (1.00000,0.75294,0.79608);
const GltColor pink1               (1.00000,0.70980,0.77255);
const GltColor pink2               (0.93333,0.66275,0.72157);
const GltColor pink3               (0.80392,0.56863,0.61961);
const GltColor pink4               (0.54510,0.38824,0.42353);
const GltColor plum                (0.86667,0.62745,0.86667);
const GltColor plum1               (1.00000,0.73333,1.00000);
const GltColor plum2               (0.93333,0.68235,0.93333);
const GltColor plum3               (0.80392,0.58824,0.80392);
const GltColor plum4               (0.54510,0.40000,0.54510);
const GltColor powderBlue          (0.69020,0.87843,0.90196);
const GltColor purple              (0.62745,0.12549,0.94118);
const GltColor purple1             (0.60784,0.18824,1.00000);
const GltColor purple2             (0.56863,0.17255,0.93333);
const GltColor purple3             (0.49020,0.14902,0.80392);
const GltColor purple4             (0.33333,0.10196,0.54510);
const GltColor red                 (1.00000,0.00000,0.00000);
const GltColor red1                (1.00000,0.00000,0.00000);
const GltColor red2                (0.93333,0.00000,0.00000);
const GltColor red3                (0.80392,0.00000,0.00000);
const GltColor red4                (0.54510,0.00000,0.00000);
const GltColor rosyBrown           (0.73725,0.56078,0.56078);
const GltColor rosyBrown1          (1.00000,0.75686,0.75686);
const GltColor rosyBrown2          (0.93333,0.70588,0.70588);
const GltColor rosyBrown3          (0.80392,0.60784,0.60784);
const GltColor rosyBrown4          (0.54510,0.41176,0.41176);
const GltColor royalBlue           (0.25490,0.41176,0.88235);
const GltColor royalBlue1          (0.28235,0.46275,1.00000);
const GltColor royalBlue2          (0.26275,0.43137,0.93333);
const GltColor royalBlue3          (0.22745,0.37255,0.80392);
const GltColor royalBlue4          (0.15294,0.25098,0.54510);
const GltColor saddleBrown         (0.54510,0.27059,0.07451);
const GltColor salmon              (0.98039,0.50196,0.44706);
const GltColor salmon1             (1.00000,0.54902,0.41176);
const GltColor salmon2             (0.93333,0.50980,0.38431);
const GltColor salmon3             (0.80392,0.43922,0.32941);
const GltColor salmon4             (0.54510,0.29804,0.22353);
const GltColor sandyBrown          (0.95686,0.64314,0.37647);
const GltColor seaGreen            (0.18039,0.54510,0.34118);
const GltColor seaGreen1           (0.32941,1.00000,0.62353);
const GltColor seaGreen2           (0.30588,0.93333,0.58039);
const GltColor seaGreen3           (0.26275,0.80392,0.50196);
const GltColor seaGreen4           (0.18039,0.54510,0.34118);
const GltColor seashell            (1.00000,0.96078,0.93333);
const GltColor seashell1           (1.00000,0.96078,0.93333);
const GltColor seashell2           (0.93333,0.89804,0.87059);
const GltColor seashell3           (0.80392,0.77255,0.74902);
const GltColor seashell4           (0.54510,0.52549,0.50980);
const GltColor sienna              (0.62745,0.32157,0.17647);
const GltColor sienna1             (1.00000,0.50980,0.27843);
const GltColor sienna2             (0.93333,0.47451,0.25882);
const GltColor sienna3             (0.80392,0.40784,0.22353);
const GltColor sienna4             (0.54510,0.27843,0.14902);
const GltColor skyBlue             (0.52941,0.80784,0.92157);
const GltColor skyBlue1            (0.52941,0.80784,1.00000);
const GltColor skyBlue2            (0.49412,0.75294,0.93333);
const GltColor skyBlue3            (0.42353,0.65098,0.80392);
const GltColor skyBlue4            (0.29020,0.43922,0.54510);
const GltColor slateBlue           (0.41569,0.35294,0.80392);
const GltColor slateBlue1          (0.51373,0.43529,1.00000);
const GltColor slateBlue2          (0.47843,0.40392,0.93333);
const GltColor slateBlue3          (0.41176,0.34902,0.80392);
const GltColor slateBlue4          (0.27843,0.23529,0.54510);
const GltColor slateGray           (0.43922,0.50196,0.56471);
const GltColor slateGray1          (0.77647,0.88627,1.00000);
const GltColor slateGray2          (0.72549,0.82745,0.93333);
const GltColor slateGray3          (0.62353,0.71373,0.80392);
const GltColor slateGray4          (0.42353,0.48235,0.54510);
const GltColor slateGrey           (0.43922,0.50196,0.56471);
const GltColor snow                (1.00000,0.98039,0.98039);
const GltColor snow1               (1.00000,0.98039,0.98039);
const GltColor snow2               (0.93333,0.91373,0.91373);
const GltColor snow3               (0.80392,0.78824,0.78824);
const GltColor snow4               (0.54510,0.53725,0.53725);
const GltColor springGreen         (0.00000,1.00000,0.49804);
const GltColor springGreen1        (0.00000,1.00000,0.49804);
const GltColor springGreen2        (0.00000,0.93333,0.46275);
const GltColor springGreen3        (0.00000,0.80392,0.40000);
const GltColor springGreen4        (0.00000,0.54510,0.27059);
const GltColor steelBlue           (0.27451,0.50980,0.70588);
const GltColor steelBlue1          (0.38824,0.72157,1.00000);
const GltColor steelBlue2          (0.36078,0.67451,0.93333);
const GltColor steelBlue3          (0.30980,0.58039,0.80392);
const GltColor steelBlue4          (0.21176,0.39216,0.54510);
const GltColor tan1                (1.00000,0.64706,0.30980);
const GltColor tan2                (0.93333,0.60392,0.28627);
const GltColor tan3                (0.80392,0.52157,0.24706);
const GltColor tan4                (0.54510,0.35294,0.16863);
const GltColor thistle             (0.84706,0.74902,0.84706);
const GltColor thistle1            (1.00000,0.88235,1.00000);
const GltColor thistle2            (0.93333,0.82353,0.93333);
const GltColor thistle3            (0.80392,0.70980,0.80392);
const GltColor thistle4            (0.54510,0.48235,0.54510);
const GltColor tomato              (1.00000,0.38824,0.27843);
const GltColor tomato1             (1.00000,0.38824,0.27843);
const GltColor tomato2             (0.93333,0.36078,0.25882);
const GltColor tomato3             (0.80392,0.30980,0.22353);
const GltColor tomato4             (0.54510,0.21176,0.14902);
const GltColor turquoise           (0.25098,0.87843,0.81569);
const GltColor turquoise1          (0.00000,0.96078,1.00000);
const GltColor turquoise2          (0.00000,0.89804,0.93333);
const GltColor turquoise3          (0.00000,0.77255,0.80392);
const GltColor turquoise4          (0.00000,0.52549,0.54510);
const GltColor violet              (0.93333,0.50980,0.93333);
const GltColor violetRed           (0.81569,0.12549,0.56471);
const GltColor violetRed1          (1.00000,0.24314,0.58824);
const GltColor violetRed2          (0.93333,0.22745,0.54902);
const GltColor violetRed3          (0.80392,0.19608,0.47059);
const GltColor violetRed4          (0.54510,0.13333,0.32157);
const GltColor wheat               (0.96078,0.87059,0.70196);
const GltColor wheat1              (1.00000,0.90588,0.72941);
const GltColor wheat2              (0.93333,0.84706,0.68235);
const GltColor wheat3              (0.80392,0.72941,0.58824);
const GltColor wheat4              (0.54510,0.49412,0.40000);
const GltColor white               (1.00000,1.00000,1.00000);
const GltColor whiteSmoke          (0.96078,0.96078,0.96078);
const GltColor yellow              (1.00000,1.00000,0.00000);
const GltColor yellow1             (1.00000,1.00000,0.00000);
const GltColor yellow2             (0.93333,0.93333,0.00000);
const GltColor yellow3             (0.80392,0.80392,0.00000);
const GltColor yellow4             (0.54510,0.54510,0.00000);
const GltColor yellowGreen         (0.60392,0.80392,0.19608);

const int   GltColor::_rgbSize = 656;

const char *GltColor::_rgbName[656] =
{
	"aliceBlue",
	"antiqueWhite",
	"antiqueWhite1",
	"antiqueWhite2",
	"antiqueWhite3",
	"antiqueWhite4",
	"aquamarine",
	"aquamarine1",
	"aquamarine2",
	"aquamarine3",
	"aquamarine4",
	"azure",
	"azure1",
	"azure2",
	"azure3",
	"azure4",
	"beige",
	"bisque",
	"bisque1",
	"bisque2",
	"bisque3",
	"bisque4",
	"black",
	"blanchedAlmond",
	"blue",
	"blue1",
	"blue2",
	"blue3",
	"blue4",
	"blueViolet",
	"brown",
	"brown1",
	"brown2",
	"brown3",
	"brown4",
	"burlywood",
	"burlywood1",
	"burlywood2",
	"burlywood3",
	"burlywood4",
	"cadetBlue",
	"cadetBlue1",
	"cadetBlue2",
	"cadetBlue3",
	"cadetBlue4",
	"chartreuse",
	"chartreuse1",
	"chartreuse2",
	"chartreuse3",
	"chartreuse4",
	"chocolate",
	"chocolate1",
	"chocolate2",
	"chocolate3",
	"chocolate4",
	"coral",
	"coral1",
	"coral2",
	"coral3",
	"coral4",
	"cornflowerBlue",
	"cornsilk",
	"cornsilk1",
	"cornsilk2",
	"cornsilk3",
	"cornsilk4",
	"cyan",
	"cyan1",
	"cyan2",
	"cyan3",
	"cyan4",
	"darkBlue",
	"darkCyan",
	"darkGoldenrod",
	"darkGoldenrod1",
	"darkGoldenrod2",
	"darkGoldenrod3",
	"darkGoldenrod4",
	"darkGray",
	"darkGreen",
	"darkGrey",
	"darkKhaki",
	"darkMagenta",
	"darkOliveGreen",
	"darkOliveGreen1",
	"darkOliveGreen2",
	"darkOliveGreen3",
	"darkOliveGreen4",
	"darkOrange",
	"darkOrange1",
	"darkOrange2",
	"darkOrange3",
	"darkOrange4",
	"darkOrchid",
	"darkOrchid1",
	"darkOrchid2",
	"darkOrchid3",
	"darkOrchid4",
	"darkRed",
	"darkSalmon",
	"darkSeaGreen",
	"darkSeaGreen1",
	"darkSeaGreen2",
	"darkSeaGreen3",
	"darkSeaGreen4",
	"darkSlateBlue",
	"darkSlateGray",
	"darkSlateGray1",
	"darkSlateGray2",
	"darkSlateGray3",
	"darkSlateGray4",
	"darkSlateGrey",
	"darkTurquoise",
	"darkViolet",
	"deepPink",
	"deepPink1",
	"deepPink2",
	"deepPink3",
	"deepPink4",
	"deepSkyBlue",
	"deepSkyBlue1",
	"deepSkyBlue2",
	"deepSkyBlue3",
	"deepSkyBlue4",
	"dimGray",
	"dimGrey",
	"dodgerBlue",
	"dodgerBlue1",
	"dodgerBlue2",
	"dodgerBlue3",
	"dodgerBlue4",
	"firebrick",
	"firebrick1",
	"firebrick2",
	"firebrick3",
	"firebrick4",
	"floralWhite",
	"forestGreen",
	"gainsboro",
	"ghostWhite",
	"gold",
	"gold1",
	"gold2",
	"gold3",
	"gold4",
	"goldenrod",
	"goldenrod1",
	"goldenrod2",
	"goldenrod3",
	"goldenrod4",
	"gray",
	"gray0",
	"gray1",
	"gray10",
	"gray100",
	"gray11",
	"gray12",
	"gray13",
	"gray14",
	"gray15",
	"gray16",
	"gray17",
	"gray18",
	"gray19",
	"gray2",
	"gray20",
	"gray21",
	"gray22",
	"gray23",
	"gray24",
	"gray25",
	"gray26",
	"gray27",
	"gray28",
	"gray29",
	"gray3",
	"gray30",
	"gray31",
	"gray32",
	"gray33",
	"gray34",
	"gray35",
	"gray36",
	"gray37",
	"gray38",
	"gray39",
	"gray4",
	"gray40",
	"gray41",
	"gray42",
	"gray43",
	"gray44",
	"gray45",
	"gray46",
	"gray47",
	"gray48",
	"gray49",
	"gray5",
	"gray50",
	"gray51",
	"gray52",
	"gray53",
	"gray54",
	"gray55",
	"gray56",
	"gray57",
	"gray58",
	"gray59",
	"gray6",
	"gray60",
	"gray61",
	"gray62",
	"gray63",
	"gray64",
	"gray65",
	"gray66",
	"gray67",
	"gray68",
	"gray69",
	"gray7",
	"gray70",
	"gray71",
	"gray72",
	"gray73",
	"gray74",
	"gray75",
	"gray76",
	"gray77",
	"gray78",
	"gray79",
	"gray8",
	"gray80",
	"gray81",
	"gray82",
	"gray83",
	"gray84",
	"gray85",
	"gray86",
	"gray87",
	"gray88",
	"gray89",
	"gray9",
	"gray90",
	"gray91",
	"gray92",
	"gray93",
	"gray94",
	"gray95",
	"gray96",
	"gray97",
	"gray98",
	"gray99",
	"green",
	"green1",
	"green2",
	"green3",
	"green4",
	"greenYellow",
	"grey",
	"grey0",
	"grey1",
	"grey10",
	"grey100",
	"grey11",
	"grey12",
	"grey13",
	"grey14",
	"grey15",
	"grey16",
	"grey17",
	"grey18",
	"grey19",
	"grey2",
	"grey20",
	"grey21",
	"grey22",
	"grey23",
	"grey24",
	"grey25",
	"grey26",
	"grey27",
	"grey28",
	"grey29",
	"grey3",
	"grey30",
	"grey31",
	"grey32",
	"grey33",
	"grey34",
	"grey35",
	"grey36",
	"grey37",
	"grey38",
	"grey39",
	"grey4",
	"grey40",
	"grey41",
	"grey42",
	"grey43",
	"grey44",
	"grey45",
	"grey46",
	"grey47",
	"grey48",
	"grey49",
	"grey5",
	"grey50",
	"grey51",
	"grey52",
	"grey53",
	"grey54",
	"grey55",
	"grey56",
	"grey57",
	"grey58",
	"grey59",
	"grey6",
	"grey60",
	"grey61",
	"grey62",
	"grey63",
	"grey64",
	"grey65",
	"grey66",
	"grey67",
	"grey68",
	"grey69",
	"grey7",
	"grey70",
	"grey71",
	"grey72",
	"grey73",
	"grey74",
	"grey75",
	"grey76",
	"grey77",
	"grey78",
	"grey79",
	"grey8",
	"grey80",
	"grey81",
	"grey82",
	"grey83",
	"grey84",
	"grey85",
	"grey86",
	"grey87",
	"grey88",
	"grey89",
	"grey9",
	"grey90",
	"grey91",
	"grey92",
	"grey93",
	"grey94",
	"grey95",
	"grey96",
	"grey97",
	"grey98",
	"grey99",
	"honeydew",
	"honeydew1",
	"honeydew2",
	"honeydew3",
	"honeydew4",
	"hotPink",
	"hotPink1",
	"hotPink2",
	"hotPink3",
	"hotPink4",
	"indianRed",
	"indianRed1",
	"indianRed2",
	"indianRed3",
	"indianRed4",
	"ivory",
	"ivory1",
	"ivory2",
	"ivory3",
	"ivory4",
	"khaki",
	"khaki1",
	"khaki2",
	"khaki3",
	"khaki4",
	"lavender",
	"lavenderBlush",
	"lavenderBlush1",
	"lavenderBlush2",
	"lavenderBlush3",
	"lavenderBlush4",
	"lawnGreen",
	"lemonChiffon",
	"lemonChiffon1",
	"lemonChiffon2",
	"lemonChiffon3",
	"lemonChiffon4",
	"lightBlue",
	"lightBlue1",
	"lightBlue2",
	"lightBlue3",
	"lightBlue4",
	"lightCoral",
	"lightCyan",
	"lightCyan1",
	"lightCyan2",
	"lightCyan3",
	"lightCyan4",
	"lightGoldenrod",
	"lightGoldenrod1",
	"lightGoldenrod2",
	"lightGoldenrod3",
	"lightGoldenrod4",
	"lightGoldenrodYellow",
	"lightGray",
	"lightGreen",
	"lightGrey",
	"lightPink",
	"lightPink1",
	"lightPink2",
	"lightPink3",
	"lightPink4",
	"lightSalmon",
	"lightSalmon1",
	"lightSalmon2",
	"lightSalmon3",
	"lightSalmon4",
	"lightSeaGreen",
	"lightSkyBlue",
	"lightSkyBlue1",
	"lightSkyBlue2",
	"lightSkyBlue3",
	"lightSkyBlue4",
	"lightSlateBlue",
	"lightSlateGray",
	"lightSlateGrey",
	"lightSteelBlue",
	"lightSteelBlue1",
	"lightSteelBlue2",
	"lightSteelBlue3",
	"lightSteelBlue4",
	"lightYellow",
	"lightYellow1",
	"lightYellow2",
	"lightYellow3",
	"lightYellow4",
	"limeGreen",
	"linen",
	"magenta",
	"magenta1",
	"magenta2",
	"magenta3",
	"magenta4",
	"maroon",
	"maroon1",
	"maroon2",
	"maroon3",
	"maroon4",
	"mediumAquamarine",
	"mediumBlue",
	"mediumOrchid",
	"mediumOrchid1",
	"mediumOrchid2",
	"mediumOrchid3",
	"mediumOrchid4",
	"mediumPurple",
	"mediumPurple1",
	"mediumPurple2",
	"mediumPurple3",
	"mediumPurple4",
	"mediumSeaGreen",
	"mediumSlateBlue",
	"mediumSpringGreen",
	"mediumTurquoise",
	"mediumVioletRed",
	"midnightBlue",
	"mintCream",
	"mistyRose",
	"mistyRose1",
	"mistyRose2",
	"mistyRose3",
	"mistyRose4",
	"moccasin",
	"navajoWhite",
	"navajoWhite1",
	"navajoWhite2",
	"navajoWhite3",
	"navajoWhite4",
	"navy",
	"navyBlue",
	"oldLace",
	"oliveDrab",
	"oliveDrab1",
	"oliveDrab2",
	"oliveDrab3",
	"oliveDrab4",
	"orange",
	"orange1",
	"orange2",
	"orange3",
	"orange4",
	"orangeRed",
	"orangeRed1",
	"orangeRed2",
	"orangeRed3",
	"orangeRed4",
	"orchid",
	"orchid1",
	"orchid2",
	"orchid3",
	"orchid4",
	"paleGoldenrod",
	"paleGreen",
	"paleGreen1",
	"paleGreen2",
	"paleGreen3",
	"paleGreen4",
	"paleTurquoise",
	"paleTurquoise1",
	"paleTurquoise2",
	"paleTurquoise3",
	"paleTurquoise4",
	"paleVioletRed",
	"paleVioletRed1",
	"paleVioletRed2",
	"paleVioletRed3",
	"paleVioletRed4",
	"papayaWhip",
	"peachPuff",
	"peachPuff1",
	"peachPuff2",
	"peachPuff3",
	"peachPuff4",
	"peru",
	"pink",
	"pink1",
	"pink2",
	"pink3",
	"pink4",
	"plum",
	"plum1",
	"plum2",
	"plum3",
	"plum4",
	"powderBlue",
	"purple",
	"purple1",
	"purple2",
	"purple3",
	"purple4",
	"red",
	"red1",
	"red2",
	"red3",
	"red4",
	"rosyBrown",
	"rosyBrown1",
	"rosyBrown2",
	"rosyBrown3",
	"rosyBrown4",
	"royalBlue",
	"royalBlue1",
	"royalBlue2",
	"royalBlue3",
	"royalBlue4",
	"saddleBrown",
	"salmon",
	"salmon1",
	"salmon2",
	"salmon3",
	"salmon4",
	"sandyBrown",
	"seaGreen",
	"seaGreen1",
	"seaGreen2",
	"seaGreen3",
	"seaGreen4",
	"seashell",
	"seashell1",
	"seashell2",
	"seashell3",
	"seashell4",
	"sienna",
	"sienna1",
	"sienna2",
	"sienna3",
	"sienna4",
	"skyBlue",
	"skyBlue1",
	"skyBlue2",
	"skyBlue3",
	"skyBlue4",
	"slateBlue",
	"slateBlue1",
	"slateBlue2",
	"slateBlue3",
	"slateBlue4",
	"slateGray",
	"slateGray1",
	"slateGray2",
	"slateGray3",
	"slateGray4",
	"slateGrey",
	"snow",
	"snow1",
	"snow2",
	"snow3",
	"snow4",
	"springGreen",
	"springGreen1",
	"springGreen2",
	"springGreen3",
	"springGreen4",
	"steelBlue",
	"steelBlue1",
	"steelBlue2",
	"steelBlue3",
	"steelBlue4",
	"tan1",
	"tan2",
	"tan3",
	"tan4",
	"thistle",
	"thistle1",
	"thistle2",
	"thistle3",
	"thistle4",
	"tomato",
	"tomato1",
	"tomato2",
	"tomato3",
	"tomato4",
	"turquoise",
	"turquoise1",
	"turquoise2",
	"turquoise3",
	"turquoise4",
	"violet",
	"violetRed",
	"violetRed1",
	"violetRed2",
	"violetRed3",
	"violetRed4",
	"wheat",
	"wheat1",
	"wheat2",
	"wheat3",
	"wheat4",
	"white",
	"whiteSmoke",
	"yellow",
	"yellow1",
	"yellow2",
	"yellow3",
	"yellow4",
	"yellowGreen"
};

const GltColor *GltColor::_rgbValue[656] =
{
	&::aliceBlue,
	&::antiqueWhite,
	&::antiqueWhite1,
	&::antiqueWhite2,
	&::antiqueWhite3,
	&::antiqueWhite4,
	&::aquamarine,
	&::aquamarine1,
	&::aquamarine2,
	&::aquamarine3,
	&::aquamarine4,
	&::azure,
	&::azure1,
	&::azure2,
	&::azure3,
	&::azure4,
	&::beige,
	&::bisque,
	&::bisque1,
	&::bisque2,
	&::bisque3,
	&::bisque4,
	&::black,
	&::blanchedAlmond,
	&::blue,
	&::blue1,
	&::blue2,
	&::blue3,
	&::blue4,
	&::blueViolet,
	&::brown,
	&::brown1,
	&::brown2,
	&::brown3,
	&::brown4,
	&::burlywood,
	&::burlywood1,
	&::burlywood2,
	&::burlywood3,
	&::burlywood4,
	&::cadetBlue,
	&::cadetBlue1,
	&::cadetBlue2,
	&::cadetBlue3,
	&::cadetBlue4,
	&::chartreuse,
	&::chartreuse1,
	&::chartreuse2,
	&::chartreuse3,
	&::chartreuse4,
	&::chocolate,
	&::chocolate1,
	&::chocolate2,
	&::chocolate3,
	&::chocolate4,
	&::coral,
	&::coral1,
	&::coral2,
	&::coral3,
	&::coral4,
	&::cornflowerBlue,
	&::cornsilk,
	&::cornsilk1,
	&::cornsilk2,
	&::cornsilk3,
	&::cornsilk4,
	&::cyan,
	&::cyan1,
	&::cyan2,
	&::cyan3,
	&::cyan4,
	&::darkBlue,
	&::darkCyan,
	&::darkGoldenrod,
	&::darkGoldenrod1,
	&::darkGoldenrod2,
	&::darkGoldenrod3,
	&::darkGoldenrod4,
	&::darkGray,
	&::darkGreen,
	&::darkGrey,
	&::darkKhaki,
	&::darkMagenta,
	&::darkOliveGreen,
	&::darkOliveGreen1,
	&::darkOliveGreen2,
	&::darkOliveGreen3,
	&::darkOliveGreen4,
	&::darkOrange,
	&::darkOrange1,
	&::darkOrange2,
	&::darkOrange3,
	&::darkOrange4,
	&::darkOrchid,
	&::darkOrchid1,
	&::darkOrchid2,
	&::darkOrchid3,
	&::darkOrchid4,
	&::darkRed,
	&::darkSalmon,
	&::darkSeaGreen,
	&::darkSeaGreen1,
	&::darkSeaGreen2,
	&::darkSeaGreen3,
	&::darkSeaGreen4,
	&::darkSlateBlue,
	&::darkSlateGray,
	&::darkSlateGray1,
	&::darkSlateGray2,
	&::darkSlateGray3,
	&::darkSlateGray4,
	&::darkSlateGrey,
	&::darkTurquoise,
	&::darkViolet,
	&::deepPink,
	&::deepPink1,
	&::deepPink2,
	&::deepPink3,
	&::deepPink4,
	&::deepSkyBlue,
	&::deepSkyBlue1,
	&::deepSkyBlue2,
	&::deepSkyBlue3,
	&::deepSkyBlue4,
	&::dimGray,
	&::dimGrey,
	&::dodgerBlue,
	&::dodgerBlue1,
	&::dodgerBlue2,
	&::dodgerBlue3,
	&::dodgerBlue4,
	&::firebrick,
	&::firebrick1,
	&::firebrick2,
	&::firebrick3,
	&::firebrick4,
	&::floralWhite,
	&::forestGreen,
	&::gainsboro,
	&::ghostWhite,
	&::gold,
	&::gold1,
	&::gold2,
	&::gold3,
	&::gold4,
	&::goldenrod,
	&::goldenrod1,
	&::goldenrod2,
	&::goldenrod3,
	&::goldenrod4,
	&::gray,
	&::gray0,
	&::gray1,
	&::gray10,
	&::gray100,
	&::gray11,
	&::gray12,
	&::gray13,
	&::gray14,
	&::gray15,
	&::gray16,
	&::gray17,
	&::gray18,
	&::gray19,
	&::gray2,
	&::gray20,
	&::gray21,
	&::gray22,
	&::gray23,
	&::gray24,
	&::gray25,
	&::gray26,
	&::gray27,
	&::gray28,
	&::gray29,
	&::gray3,
	&::gray30,
	&::gray31,
	&::gray32,
	&::gray33,
	&::gray34,
	&::gray35,
	&::gray36,
	&::gray37,
	&::gray38,
	&::gray39,
	&::gray4,
	&::gray40,
	&::gray41,
	&::gray42,
	&::gray43,
	&::gray44,
	&::gray45,
	&::gray46,
	&::gray47,
	&::gray48,
	&::gray49,
	&::gray5,
	&::gray50,
	&::gray51,
	&::gray52,
	&::gray53,
	&::gray54,
	&::gray55,
	&::gray56,
	&::gray57,
	&::gray58,
	&::gray59,
	&::gray6,
	&::gray60,
	&::gray61,
	&::gray62,
	&::gray63,
	&::gray64,
	&::gray65,
	&::gray66,
	&::gray67,
	&::gray68,
	&::gray69,
	&::gray7,
	&::gray70,
	&::gray71,
	&::gray72,
	&::gray73,
	&::gray74,
	&::gray75,
	&::gray76,
	&::gray77,
	&::gray78,
	&::gray79,
	&::gray8,
	&::gray80,
	&::gray81,
	&::gray82,
	&::gray83,
	&::gray84,
	&::gray85,
	&::gray86,
	&::gray87,
	&::gray88,
	&::gray89,
	&::gray9,
	&::gray90,
	&::gray91,
	&::gray92,
	&::gray93,
	&::gray94,
	&::gray95,
	&::gray96,
	&::gray97,
	&::gray98,
	&::gray99,
	&::green,
	&::green1,
	&::green2,
	&::green3,
	&::green4,
	&::greenYellow,
	&::grey,
	&::grey0,
	&::grey1,
	&::grey10,
	&::grey100,
	&::grey11,
	&::grey12,
	&::grey13,
	&::grey14,
	&::grey15,
	&::grey16,
	&::grey17,
	&::grey18,
	&::grey19,
	&::grey2,
	&::grey20,
	&::grey21,
	&::grey22,
	&::grey23,
	&::grey24,
	&::grey25,
	&::grey26,
	&::grey27,
	&::grey28,
	&::grey29,
	&::grey3,
	&::grey30,
	&::grey31,
	&::grey32,
	&::grey33,
	&::grey34,
	&::grey35,
	&::grey36,
	&::grey37,
	&::grey38,
	&::grey39,
	&::grey4,
	&::grey40,
	&::grey41,
	&::grey42,
	&::grey43,
	&::grey44,
	&::grey45,
	&::grey46,
	&::grey47,
	&::grey48,
	&::grey49,
	&::grey5,
	&::grey50,
	&::grey51,
	&::grey52,
	&::grey53,
	&::grey54,
	&::grey55,
	&::grey56,
	&::grey57,
	&::grey58,
	&::grey59,
	&::grey6,
	&::grey60,
	&::grey61,
	&::grey62,
	&::grey63,
	&::grey64,
	&::grey65,
	&::grey66,
	&::grey67,
	&::grey68,
	&::grey69,
	&::grey7,
	&::grey70,
	&::grey71,
	&::grey72,
	&::grey73,
	&::grey74,
	&::grey75,
	&::grey76,
	&::grey77,
	&::grey78,
	&::grey79,
	&::grey8,
	&::grey80,
	&::grey81,
	&::grey82,
	&::grey83,
	&::grey84,
	&::grey85,
	&::grey86,
	&::grey87,
	&::grey88,
	&::grey89,
	&::grey9,
	&::grey90,
	&::grey91,
	&::grey92,
	&::grey93,
	&::grey94,
	&::grey95,
	&::grey96,
	&::grey97,
	&::grey98,
	&::grey99,
	&::honeydew,
	&::honeydew1,
	&::honeydew2,
	&::honeydew3,
	&::honeydew4,
	&::hotPink,
	&::hotPink1,
	&::hotPink2,
	&::hotPink3,
	&::hotPink4,
	&::indianRed,
	&::indianRed1,
	&::indianRed2,
	&::indianRed3,
	&::indianRed4,
	&::ivory,
	&::ivory1,
	&::ivory2,
	&::ivory3,
	&::ivory4,
	&::khaki,
	&::khaki1,
	&::khaki2,
	&::khaki3,
	&::khaki4,
	&::lavender,
	&::lavenderBlush,
	&::lavenderBlush1,
	&::lavenderBlush2,
	&::lavenderBlush3,
	&::lavenderBlush4,
	&::lawnGreen,
	&::lemonChiffon,
	&::lemonChiffon1,
	&::lemonChiffon2,
	&::lemonChiffon3,
	&::lemonChiffon4,
	&::lightBlue,
	&::lightBlue1,
	&::lightBlue2,
	&::lightBlue3,
	&::lightBlue4,
	&::lightCoral,
	&::lightCyan,
	&::lightCyan1,
	&::lightCyan2,
	&::lightCyan3,
	&::lightCyan4,
	&::lightGoldenrod,
	&::lightGoldenrod1,
	&::lightGoldenrod2,
	&::lightGoldenrod3,
	&::lightGoldenrod4,
	&::lightGoldenrodYellow,
	&::lightGray,
	&::lightGreen,
	&::lightGrey,
	&::lightPink,
	&::lightPink1,
	&::lightPink2,
	&::lightPink3,
	&::lightPink4,
	&::lightSalmon,
	&::lightSalmon1,
	&::lightSalmon2,
	&::lightSalmon3,
	&::lightSalmon4,
	&::lightSeaGreen,
	&::lightSkyBlue,
	&::lightSkyBlue1,
	&::lightSkyBlue2,
	&::lightSkyBlue3,
	&::lightSkyBlue4,
	&::lightSlateBlue,
	&::lightSlateGray,
	&::lightSlateGrey,
	&::lightSteelBlue,
	&::lightSteelBlue1,
	&::lightSteelBlue2,
	&::lightSteelBlue3,
	&::lightSteelBlue4,
	&::lightYellow,
	&::lightYellow1,
	&::lightYellow2,
	&::lightYellow3,
	&::lightYellow4,
	&::limeGreen,
	&::linen,
	&::magenta,
	&::magenta1,
	&::magenta2,
	&::magenta3,
	&::magenta4,
	&::maroon,
	&::maroon1,
	&::maroon2,
	&::maroon3,
	&::maroon4,
	&::mediumAquamarine,
	&::mediumBlue,
	&::mediumOrchid,
	&::mediumOrchid1,
	&::mediumOrchid2,
	&::mediumOrchid3,
	&::mediumOrchid4,
	&::mediumPurple,
	&::mediumPurple1,
	&::mediumPurple2,
	&::mediumPurple3,
	&::mediumPurple4,
	&::mediumSeaGreen,
	&::mediumSlateBlue,
	&::mediumSpringGreen,
	&::mediumTurquoise,
	&::mediumVioletRed,
	&::midnightBlue,
	&::mintCream,
	&::mistyRose,
	&::mistyRose1,
	&::mistyRose2,
	&::mistyRose3,
	&::mistyRose4,
	&::moccasin,
	&::navajoWhite,
	&::navajoWhite1,
	&::navajoWhite2,
	&::navajoWhite3,
	&::navajoWhite4,
	&::navy,
	&::navyBlue,
	&::oldLace,
	&::oliveDrab,
	&::oliveDrab1,
	&::oliveDrab2,
	&::oliveDrab3,
	&::oliveDrab4,
	&::orange,
	&::orange1,
	&::orange2,
	&::orange3,
	&::orange4,
	&::orangeRed,
	&::orangeRed1,
	&::orangeRed2,
	&::orangeRed3,
	&::orangeRed4,
	&::orchid,
	&::orchid1,
	&::orchid2,
	&::orchid3,
	&::orchid4,
	&::paleGoldenrod,
	&::paleGreen,
	&::paleGreen1,
	&::paleGreen2,
	&::paleGreen3,
	&::paleGreen4,
	&::paleTurquoise,
	&::paleTurquoise1,
	&::paleTurquoise2,
	&::paleTurquoise3,
	&::paleTurquoise4,
	&::paleVioletRed,
	&::paleVioletRed1,
	&::paleVioletRed2,
	&::paleVioletRed3,
	&::paleVioletRed4,
	&::papayaWhip,
	&::peachPuff,
	&::peachPuff1,
	&::peachPuff2,
	&::peachPuff3,
	&::peachPuff4,
	&::peru,
	&::pink,
	&::pink1,
	&::pink2,
	&::pink3,
	&::pink4,
	&::plum,
	&::plum1,
	&::plum2,
	&::plum3,
	&::plum4,
	&::powderBlue,
	&::purple,
	&::purple1,
	&::purple2,
	&::purple3,
	&::purple4,
	&::red,
	&::red1,
	&::red2,
	&::red3,
	&::red4,
	&::rosyBrown,
	&::rosyBrown1,
	&::rosyBrown2,
	&::rosyBrown3,
	&::rosyBrown4,
	&::royalBlue,
	&::royalBlue1,
	&::royalBlue2,
	&::royalBlue3,
	&::royalBlue4,
	&::saddleBrown,
	&::salmon,
	&::salmon1,
	&::salmon2,
	&::salmon3,
	&::salmon4,
	&::sandyBrown,
	&::seaGreen,
	&::seaGreen1,
	&::seaGreen2,
	&::seaGreen3,
	&::seaGreen4,
	&::seashell,
	&::seashell1,
	&::seashell2,
	&::seashell3,
	&::seashell4,
	&::sienna,
	&::sienna1,
	&::sienna2,
	&::sienna3,
	&::sienna4,
	&::skyBlue,
	&::skyBlue1,
	&::skyBlue2,
	&::skyBlue3,
	&::skyBlue4,
	&::slateBlue,
	&::slateBlue1,
	&::slateBlue2,
	&::slateBlue3,
	&::slateBlue4,
	&::slateGray,
	&::slateGray1,
	&::slateGray2,
	&::slateGray3,
	&::slateGray4,
	&::slateGrey,
	&::snow,
	&::snow1,
	&::snow2,
	&::snow3,
	&::snow4,
	&::springGreen,
	&::springGreen1,
	&::springGreen2,
	&::springGreen3,
	&::springGreen4,
	&::steelBlue,
	&::steelBlue1,
	&::steelBlue2,
	&::steelBlue3,
	&::steelBlue4,
	&::tan1,
	&::tan2,
	&::tan3,
	&::tan4,
	&::thistle,
	&::thistle1,
	&::thistle2,
	&::thistle3,
	&::thistle4,
	&::tomato,
	&::tomato1,
	&::tomato2,
	&::tomato3,
	&::tomato4,
	&::turquoise,
	&::turquoise1,
	&::turquoise2,
	&::turquoise3,
	&::turquoise4,
	&::violet,
	&::violetRed,
	&::violetRed1,
	&::violetRed2,
	&::violetRed3,
	&::violetRed4,
	&::wheat,
	&::wheat1,
	&::wheat2,
	&::wheat3,
	&::wheat4,
	&::white,
	&::whiteSmoke,
	&::yellow,
	&::yellow1,
	&::yellow2,
	&::yellow3,
	&::yellow4,
	&::yellowGreen
};

