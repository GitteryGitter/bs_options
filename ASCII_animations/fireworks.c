#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <math.h>

#define WIDTH 120
#define HEIGHT 30 
#define MAX_PARTICLES 3000*3
#define RUN_TIME_SECONDS 15

typedef enum { LAUNCH, EXPLODE, TRAIL, INACTIVE } State;

typedef struct {
    float x, y;
    float vx, vy;
    char symbol;
    int color;
    int life;
    State state;
} Particle;

void clear_screen() { printf("\033[H\033[J"); }
void move_cursor(int x, int y) { printf("\033[%d;%dH", y, x); }
void set_color(int c) { printf("\033[38;5;%dm", c); }
void reset_color() { printf("\033[0m"); }

int find_slot(Particle p[]) {
    for (int i = 0; i < MAX_PARTICLES; i++) {
        if (p[i].state == INACTIVE) return i;
    }
    return -1;
}

int main() {
    srand(time(NULL));
    Particle p[MAX_PARTICLES];
    for (int i = 0; i < MAX_PARTICLES; i++) p[i].state = INACTIVE;

    char symbols[] = {'*', '.', 'o', '+', 'x', 's', '@'};
    int colors[] = {196, 202, 208, 214, 220, 226, 190, 154, 118, 82, 46, 47, 48, 49, 51, 39, 27, 21, 57, 93, 129, 165, 201};

    time_t start_time = time(NULL);
    printf("\033[?25l"); 

    while (time(NULL) - start_time < RUN_TIME_SECONDS) {
        clear_screen();

        // 1. Launch logic (Lowered launch height so they explode in frame)
        if (rand() % 25 == 0) {
            int slot = find_slot(p);
            if (slot != -1) {
                p[slot].state = LAUNCH;
                p[slot].x = rand() % (WIDTH - 40) + 20;
                p[slot].y = HEIGHT - 2;
                p[slot].vx = ((float)rand() / RAND_MAX - 0.5) * 0.2;
                // Stronger upward velocity to reach the middle of the screen
                p[slot].vy = -((float)rand() / RAND_MAX * 0.5 + 1.2); 
                // Explode between 1/4 and 1/2 height of the screen
                p[slot].life = 15 + rand() % 10; 
                p[slot].symbol = '*';
                // Varied shell colors - bright colors
                int shell_colors[] = {226, 220, 214, 208, 202, 196, 201, 165, 129};
                p[slot].color = shell_colors[rand() % 9];
            }
        }

        for (int i = 0; i < MAX_PARTICLES; i++) {
            if (p[i].state == INACTIVE) continue;

            // Strict boundary kill-switch
            if (p[i].x <= 1 || p[i].x >= WIDTH - 1 || p[i].y <= 1 || p[i].y >= HEIGHT - 1) {
                p[i].state = INACTIVE;
                continue;
            }

            if (p[i].state == LAUNCH) {
                // Trail Logic - use same color as shell, different symbol
                int t_slot = find_slot(p);
                if (t_slot != -1) {
                    p[t_slot].state = TRAIL;
                    p[t_slot].x = p[i].x; p[t_slot].y = p[i].y;
                    p[t_slot].life = 12;
                    p[t_slot].color = p[i].color; // Match shell color
                    p[t_slot].symbol = ':';
                }

                p[i].x += p[i].vx;
                p[i].y += p[i].vy;
                p[i].life--;

                // Force explosion if getting too close to top
                if (p[i].life <= 0 || p[i].y < 6) {
                    float cx = p[i].x;
                    float cy = p[i].y;
                    p[i].state = INACTIVE;

                    int count = 120 + rand() % 80;
                    for (int j = 0; j < count; j++) {
                        int s = find_slot(p);
                        if (s != -1) {
                            p[s].state = EXPLODE;
                            p[s].x = cx;
                            p[s].y = cy;
                            float angle = ((float)rand() / RAND_MAX) * 2.0 * M_PI;
                            float speed = ((float)rand() / RAND_MAX) * 0.8 + 0.2;
                            // FIXED: Equal horizontal and vertical components for spherical explosion
                            p[s].vx = cos(angle) * speed;
                            p[s].vy = sin(angle) * speed * 0.5; // Reduced to account for terminal aspect ratio
                            // Longer lifetime so particles have time to fall gracefully
                            p[s].life = 50 + rand() % 40;
                            p[s].symbol = symbols[rand() % 7];
                            p[s].color = colors[rand() % 23];
                        }
                    }
                } else {
                    move_cursor((int)p[i].x, (int)p[i].y);
                    set_color(p[i].color);
                    putchar(p[i].symbol);
                }
            } 
            else if (p[i].state == EXPLODE) {
                // IMPROVED PHYSICS: Immediate falling with air resistance
                p[i].x += p[i].vx;
                p[i].y += p[i].vy;
                
                // Stronger gravity so particles start falling immediately
                p[i].vy += 0.025; 
                
                // Air resistance - velocity decays over time (drag effect)
                p[i].vx *= 0.985;
                p[i].vy *= 0.985;
                
                p[i].life--;

                if (p[i].life <= 0) {
                    p[i].state = INACTIVE;
                } else {
                    move_cursor((int)p[i].x, (int)p[i].y);
                    // Gradual dimming as they fall and fade
                    if (p[i].life < 15) set_color(237);
                    else if (p[i].life < 25) set_color(240);
                    else if (p[i].life < 35) set_color(243);
                    else set_color(p[i].color);
                    putchar(p[i].symbol);
                }
            }
            else if (p[i].state == TRAIL) {
                p[i].life--;
                if (p[i].life <= 0) p[i].state = INACTIVE;
                else {
                    move_cursor((int)p[i].x, (int)p[i].y);
                    // Fade trail color based on life
                    if (p[i].life > 8) set_color(p[i].color);
                    else if (p[i].life > 4) set_color(243);
                    else set_color(236);
                    putchar(p[i].symbol);
                }
            }
        }

        fflush(stdout);
        usleep(40000); 
    }

    reset_color();
    printf("\033[?25h\033[H\033[J\n");
    return 0;
}