#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

int main(int argc, char *argv[]) {
    const char *msg = argc > 1 ? argv[1] : "START";
    int fd = open("/dev/cmachine", O_WRONLY);
    if (fd < 0) {
        perror("open");
        return 1;
    }
    int ret = write(fd, msg, strlen(msg));
    printf("Wrote %d bytes: %s\n", ret, msg);
    close(fd);
    return 0;
}
