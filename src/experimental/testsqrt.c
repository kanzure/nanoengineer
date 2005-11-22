#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <sys/vtimes.h>

#include "interp_sqrt.c"

static inline double
extendSqrt(double x)
{
    // this adds 4 nanoseconds
    // extend range to [0.01,10000]
    if (x < 1.0) {
	return 0.1 * interpolator_sqrt(100.0 * x);
    } else if (x > 100.0) {
	return 10.0 * interpolator_sqrt(0.01 * x);
    } else {
	return interpolator_sqrt(x);
    }
}

#define TIMEDIFF(late,early)  ((late).tv_sec - (early).tv_sec + \
			       1.0e-9 * ((late).tv_nsec - (early).tv_nsec))
#define ELAPSED_NANOSECONDS()   (1.e9 * TIMEDIFF(ts2, ts1) / N)

struct timespec ts1, ts2, before, after;
volatile double x, xsq, y;
#define THOUSAND  1000
#define MILLION   (THOUSAND * THOUSAND)
#define N         (100 * MILLION)
//#define N         (100 * THOUSAND)

/*
 * 0.6 to 0.7 nanoseconds for a floating-point comparison, 14
 * nanoseconds for library sqrt
 *
 * 4 nanoseconds for just the polynomial
 *
 * It takes four comparisons to get down to the polynomial, so I'd
 * assume it would take 4*0.7 + 4 nsecs = ~7 nsec for the lookup sqrt,
 * but instead it takes 11 or 12 nsecs. Why?
 *
 * The library sqrt takes 14 nsecs.
 */

int main(int argc, char **argv)
{
    int i;
    double tbaseline;

    x = 25.0;
    xsq = x * x;


    /* Reference: a loop that just does an assignment */
    clock_gettime(CLOCK_REALTIME, &before);
    clock_gettime(CLOCK_REALTIME, &ts1);
    for (i = 0; i < N; i++) {
	y = x;
    }
    clock_gettime(CLOCK_REALTIME, &ts2);
    tbaseline = ELAPSED_NANOSECONDS();


    /* Floating-point comparisons take 1.8 nsecs */
    clock_gettime(CLOCK_REALTIME, &ts1);
    for (i = 0; i < N; i++) {
	if (x > M_PI)
	    y = 0.0;
	else
	    y = 1.0;
    }
    clock_gettime(CLOCK_REALTIME, &ts2);
    printf("%f nanoseconds for float comparison\n",
	   ELAPSED_NANOSECONDS() - tbaseline);


    /* The library sqrt() function takes 14 nsecs */
    clock_gettime(CLOCK_REALTIME, &ts1);
    for (i = 0; i < N; i++) {
	y = sqrt(x);
    }
    clock_gettime(CLOCK_REALTIME, &ts2);
    printf("%f nanoseconds for library sqrt\n",
	   ELAPSED_NANOSECONDS() - tbaseline);
    printf("sqrt(%f) = %f\n", x, y);


    /* Tinker with the lookup-table sqrt until it's fast */
    clock_gettime(CLOCK_REALTIME, &ts1);
    for (i = 0; i < N; i++) {
	//y = extendSqrt(xsq);
	y = interpolator_sqrt(xsq);
    }
    clock_gettime(CLOCK_REALTIME, &ts2);
    printf("%f nanoseconds for lookup-table sqrt\n",
	   ELAPSED_NANOSECONDS() - tbaseline);
    clock_gettime(CLOCK_REALTIME, &after);
    printf("sqrtlut(%f) = %f\n", x, y);

    printf("%f seconds for the whole thing\n", TIMEDIFF(after, before));

    return 0;
}
