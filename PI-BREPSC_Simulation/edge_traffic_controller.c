#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define GREEN 0
#define YELLOW 1
#define RED 2

// 状态机结构体
typedef struct {
    int vehicle_light;
    int pedestrian_light;
    int priority; // 0: normal, 1: pedestrian_high
} TrafficController;

void set_vehicle_light(int state) {
    printf("Vehicle Light: %s\n", state==GREEN?"GREEN":state==YELLOW?"YELLOW":"RED");
}
void set_pedestrian_light(int state) {
    printf("Pedestrian Light: %s\n", state==GREEN?"WALK":state==YELLOW?"WAIT":"STOP");
}

void update_priority(TrafficController *ctrl, const char* ai_file) {
    FILE *fp = fopen(ai_file, "r");
    if (!fp) return;
    char buf[32];
    if (fgets(buf, sizeof(buf), fp)) {
        if (strstr(buf, "high")) ctrl->priority = 1;
        else ctrl->priority = 0;
    }
    fclose(fp);
}

void traffic_fsm(TrafficController *ctrl) {
    if (ctrl->priority == 1) {
        // 行人优先：切换为行人绿灯，车辆红灯
        ctrl->vehicle_light = RED;
        ctrl->pedestrian_light = GREEN;
    } else {
        // 正常：车辆绿灯，行人红灯
        ctrl->vehicle_light = GREEN;
        ctrl->pedestrian_light = RED;
    }
    set_vehicle_light(ctrl->vehicle_light);
    set_pedestrian_light(ctrl->pedestrian_light);
}

int main() {
    TrafficController ctrl = {GREEN, RED, 0};
    const char* ai_file = "ai_priority.txt";
    while (1) {
        update_priority(&ctrl, ai_file);
        traffic_fsm(&ctrl);
        sleep(2); // 2秒刷新一次
    }
    return 0;
} 