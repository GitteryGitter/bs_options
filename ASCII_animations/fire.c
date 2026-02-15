#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <math.h>

#define WIDTH 80
#define HEIGHT 30
#define RUN_TIME_SECONDS 5
#define WIND -1

const char* charset = " .:-=+*#%@";
const int charset_len = 10;

// Fire colors: Black -> Red -> Orange -> Yellow -> White
int fire_colors[] = {0, 233, 234, 52, 88, 124, 160, 196, 202, 208, 214, 220, 226, 227, 228, 229, 230, 231};
int num_colors = 18;

void hide_cursor() { printf("\033[?25l"); }
void show_cursor() { printf("\033[?25h"); }

int main() {
    srand(time(NULL));
    int fire[WIDTH * HEIGHT] = {0};
    time_t start_time = time(NULL);

    hide_cursor();

    while (time(NULL) - start_time < RUN_TIME_SECONDS) {
        printf("\033[H"); // Reset cursor to top-left
        fflush(stdout);

        // 1. Heat the bottom (Fuel Source)
        // We apply a slight fade to the source itself so it's not a solid line
        for (int x = 0; x < WIDTH; x++) {
            float dist_from_center = abs(x - WIDTH / 2) / (float)(WIDTH / 2);
            if (dist_from_center < 0.8) { // Only heat the middle 80%
                fire[(HEIGHT - 1) * WIDTH + x] = num_colors - 1;
            } else {
                fire[(HEIGHT - 1) * WIDTH + x] = 0;
            }
        }

        // 2. Diffusion Logic with WIND and EDGE FADING
        for (int y = 0; y < HEIGHT - 1; y++) {
            for (int x = 0; x < WIDTH; x++) {
                int sway = (rand() % 3) - 1; 
                int src_x = x + sway + WIND;
                int src_y = y + 1;

                if (src_x < 0) src_x = 0;
                if (src_x >= WIDTH) src_x = WIDTH - 1;

                int pixel = fire[src_y * WIDTH + src_x];
                
                // --- EDGE FADING LOGIC ---
                // Calculate how close we are to the edge (0.0 = center, 1.0 = edge)
                float edge_dist = abs(x - WIDTH / 2) / (float)(WIDTH / 2);
                
                // Increase decay based on edge distance (makes edges cool faster)
                int extra_decay = (rand() % 100 < (edge_dist * 100)) ? 1 : 0;
                int decay = (rand() % 2) + extra_decay; 

                fire[y * WIDTH + x] = (pixel - decay > 0) ? (pixel - decay) : 0;
            }
        }

        // 3. Render Frame
        for (int y = 0; y < HEIGHT; y++) {
            for (int x = 0; x < WIDTH; x++) {
                int heat = fire[y * WIDTH + x];
                
                if (heat == 0) {
                    printf(" ");
                } else {
                    int color = fire_colors[heat];
                    char c = (heat >= charset_len) ? charset[charset_len - 1] : charset[heat];
                    printf("\033[38;5;%dm%c", color, c);
                }
            }
            putchar('\n');
        }

        fflush(stdout);
        usleep(45000); 
    }

    show_cursor();
    printf("\033[0m\n");
    return 0;
}