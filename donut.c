#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <time.h> 

#define DURATION 4

int main() {
    float a = 0, e = 1, c = 1, d = 0, f, g, h, G, H, A, t, D;
    float z[1760];
    char b[1760];
    int i, j, k, x, y, o, N;

    #define R(t,x,y) f=x;x-=t*y;y+=t*f;f=(3-x*x-y*y)/2;x*=f;y*=f;

    time_t start_time = time(NULL);

    printf("\x1b[?25l\x1b[2J");

    while (difftime(time(NULL), start_time) < DURATION) {
        #ifdef _WIN32
            system("cls");
        #else
            system("clear");
        #endif

        memset(b, 32, 1760);
        memset(z, 0, 7040);
        g = 0; h = 1;

        for (j = 0; j < 90; j++) {
            G = 0; H = 1;
            for (i = 0; i < 314; i++) {
                A = h + 2; 
                D = 1 / (G * A * a + g * e + 5);
                t = G * A * e - g * a;
                x = 40 + 30 * D * (H * A * d - t * c);
                y = 12 + 15 * D * (H * A * c + t * d);
                o = x + 80 * y;
                N = 8 * ((g * a - G * h * e) * d - G * h * a - g * e - H * h * c);
                
                if (22 > y && y > 0 && x > 0 && 80 > x && D > z[o]) {
                    z[o] = D;
                    b[o] = (N > 0 ? N : 0); 
                }
                R(.02, H, G);
            }
            R(.07, h, g);
        }

        for (k = 0; k < 1761; k++) {
            if (k % 80 == 0) {
                putchar(10);
            } else {
                int intensity = b[k];
                if (intensity == 32) {
                    putchar(32);
                } else {
                    if (intensity > 9)      printf("\x1b[38;5;46m"); 
                    else if (intensity > 6) printf("\x1b[38;5;40m"); 
                    else if (intensity > 3) printf("\x1b[38;5;34m"); 
                    else                    printf("\x1b[38;5;22m"); 
                    
                    putchar(".,-~:;=!*#$@"[intensity]);
                }
            }
        }
        
        R(.04, e, a);
        R(.02, d, c);
        usleep(20000); 
    }
    printf("\x1b[0m");   
    printf("\x1b[?25h");  
    printf("\n");         
    fflush(stdout);

    return 0;
}