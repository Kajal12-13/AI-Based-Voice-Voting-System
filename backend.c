#include <stdio.h>

int main() {
    FILE *fp = fopen("votes.txt", "r");
    char vote[100];

    printf("Votes Received:\n");

    while(fgets(vote, sizeof(vote), fp)) {
        printf("%s", vote);
    }

    fclose(fp);
    return 0;
}