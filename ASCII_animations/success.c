#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <math.h>

#define WIDTH 60
#define HEIGHT 25
#define MAX_PARTICLES 500

typedef enum { LAUNCH, EXPLODE, SPARKLE, INACTIVE } State;

typedef struct {
    float x, y;
    float vx, vy;
    char symbol;
    int color;
    int life;
    int max_life;
    State state;
} Particle;

void clear_screen() { printf("\033[H\033[J"); }
void move_cursor(int x, int y) { printf("\033[%d;%dH", y, x); }
void set_color(int c) { printf("\033[38;5;%dm", c); }
void reset_color() { printf("\033[0m"); }

void draw_success_text(int frame, int neon_color, int grey_blend_color) {
    char* text = "\n                          Success!";
    

    move_cursor(1, 1);
    

    int is_bright = (frame / 10) % 2;
    int color = is_bright ? neon_color : grey_blend_color;
    
    set_color(color);
    printf("%s", text);
    reset_color();
}

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


    printf("\033[?25l");
    clear_screen();
    
 
    int neon_colors[][2] = {
        {196, 167},  
        {46, 65},   
        {201, 139},  
        {51, 67},    
        {226, 185},  
        {165, 103}   
    };
    
    int color_choice = rand() % 6;
    int neon_color = neon_colors[color_choice][0];
    int grey_blend_color = neon_colors[color_choice][1];
 
    int palette_choice = rand() % 3;
    int colors[10];
    
    if (palette_choice == 0) {
      
        int temp[] = {231, 230, 229, 228, 227, 226, 220, 214, 208, 202};
        for(int i = 0; i < 10; i++) colors[i] = temp[i];
    } else if (palette_choice == 1) {
      
        int temp[] = {231, 195, 159, 123, 87, 51, 45, 39, 33, 27};
        for(int i = 0; i < 10; i++) colors[i] = temp[i];
    } else {
   
        int temp[] = {231, 225, 219, 213, 207, 201, 200, 199, 198, 197};
        for(int i = 0; i < 10; i++) colors[i] = temp[i];
    }

    char sparkle_symbols[] = {'*', '+', 'x', 'o', '@', '#', '.', ':', ';', '~'};
    
 
    int shell = find_slot(p);
    p[shell].state = LAUNCH;
    p[shell].x = WIDTH / 2.0;
    p[shell].y = HEIGHT - 2;
    p[shell].vx = ((float)rand() / RAND_MAX - 0.5) * 0.1;
    p[shell].vy = -1.5;
    p[shell].life = 18;
    p[shell].symbol = '|';
    p[shell].color = colors[5];

    int frame = 0;
    int exploded = 0;
    
    while (1) {
        clear_screen();
        
     
        draw_success_text(frame, neon_color, grey_blend_color);
        
    
        int firework_offset_y = 3;
        
        int active_count = 0;
        
        for (int i = 0; i < MAX_PARTICLES; i++) {
            if (p[i].state == INACTIVE) continue;
            active_count++;
            
            if (p[i].x <= 0 || p[i].x >= WIDTH || p[i].y <= 0 || p[i].y >= HEIGHT) {
                p[i].state = INACTIVE;
                continue;
            }
            
            if (p[i].state == LAUNCH) {
              
                if (frame % 2 == 0) {
                    int t = find_slot(p);
                    if (t != -1) {
                        p[t].state = SPARKLE;
                        p[t].x = p[i].x + ((float)rand() / RAND_MAX - 0.5) * 0.5;
                        p[t].y = p[i].y + ((float)rand() / RAND_MAX - 0.5) * 0.5;
                        p[t].life = p[t].max_life = 8;
                        p[t].vx = p[t].vy = 0;
                        p[t].color = 243;
                        p[t].symbol = '.';
                    }
                }
                
                p[i].x += p[i].vx;
                p[i].y += p[i].vy;
                p[i].vy += 0.02; 
                p[i].life--;
                
                if (p[i].life <= 0 || p[i].y < HEIGHT / 3) {
                    float cx = p[i].x;
                    float cy = p[i].y;
                    p[i].state = INACTIVE;
                    exploded = 1;
                    
                
                    int count = 200 + rand() % 100;
                    for (int j = 0; j < count; j++) {
                        int s = find_slot(p);
                        if (s != -1) {
                            p[s].state = EXPLODE;
                            p[s].x = cx;
                            p[s].y = cy;
                            
                  
                            float angle = ((float)rand() / RAND_MAX) * 2.0 * M_PI;
                            float speed = ((float)rand() / RAND_MAX) * 1.2 + 0.3;
                            
                      
                            p[s].vx = cos(angle) * speed;
                            p[s].vy = sin(angle) * speed * 0.5;
                            
                            p[s].life = p[s].max_life = 60 + rand() % 50; 
                            p[s].symbol = sparkle_symbols[rand() % 10];
                            p[s].color = colors[rand() % 10];
                        }
                    }
                } else {
                    move_cursor((int)p[i].x, (int)p[i].y + firework_offset_y);
                    set_color(p[i].color);
                    putchar(p[i].symbol);
                }
            }
            else if (p[i].state == EXPLODE) {
                p[i].x += p[i].vx;
                p[i].y += p[i].vy;
                
              
                p[i].vy += 0.02; 
                p[i].vx *= 0.98;
                p[i].vy *= 0.98;
                
                p[i].life--;
                
                if (p[i].life <= 0) {
                    p[i].state = INACTIVE;
                } else {
                    move_cursor((int)p[i].x, (int)p[i].y + firework_offset_y);
                    
                  
                    float life_ratio = (float)p[i].life / p[i].max_life;
                    
                    if (life_ratio > 0.8) {
                        set_color(231);
                        putchar('*');
                    } else if (life_ratio > 0.6) {
                      
                        set_color(p[i].color);
                        putchar(p[i].symbol);
                    } else if (life_ratio > 0.4) {
                     
                        set_color(colors[7]);
                        putchar(p[i].symbol);
                    } else if (life_ratio > 0.2) {
                     
                        set_color(250);
                        putchar('.');
                    } else {
                      
                        set_color(240);
                        putchar('.');
                    }
                }
            }
            else if (p[i].state == SPARKLE) {
                p[i].life--;
                if (p[i].life <= 0) {
                    p[i].state = INACTIVE;
                } else {
                    move_cursor((int)p[i].x, (int)p[i].y + firework_offset_y);
                    float life_ratio = (float)p[i].life / p[i].max_life;
                    if (life_ratio > 0.5) set_color(p[i].color);
                    else set_color(236);
                    putchar(p[i].symbol);
                }
            }
        }
        
        fflush(stdout);
        usleep(50000); 
        frame++;
        
     
        if (exploded && active_count == 0) {
            usleep(500000); 
            break;
        }
    }
    
    reset_color();
    printf("\033[?25h\033[H\033[J\n");
    return 0;
}