#include <arpa/inet.h>
#include <errno.h>
#include <netdb.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>

static int set_nonblocking_local(int fd) {
    int fl = fcntl(fd, F_GETFL, 0);
    if (fl < 0) {
        return -1;
    }
    return fcntl(fd, F_SETFL, fl | O_NONBLOCK);
}

static double now_seconds(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

int main(int argc, char **argv) {
    if (argc != 5) {
        fprintf(stderr, "usage: %s <host> <port> <N_clients> <hold_seconds>\n", argv[0]);
        return 2;
    }

    const char *host = argv[1];
    int port = atoi(argv[2]);
    int n_clients = atoi(argv[3]);
    int hold_seconds = atoi(argv[4]);

    if (port <= 0 || n_clients <= 0 || hold_seconds < 0) {
        fprintf(stderr, "invalid arguments\n");
        return 2;
    }

    signal(SIGPIPE, SIG_IGN);

    struct sockaddr_in sa;
    memset(&sa, 0, sizeof(sa));
    sa.sin_family = AF_INET;
    sa.sin_port = htons((uint16_t)port);

    if (inet_pton(AF_INET, host, &sa.sin_addr) != 1) {
        struct addrinfo hints;
        memset(&hints, 0, sizeof(hints));
        hints.ai_family = AF_INET;
        hints.ai_socktype = SOCK_STREAM;

        struct addrinfo *res = NULL;
        if (getaddrinfo(host, NULL, &hints, &res) != 0 || res == NULL) {
            fprintf(stderr, "bad host: %s\n", host);
            return 2;
        }

        sa.sin_addr = ((struct sockaddr_in *)res->ai_addr)->sin_addr;
        freeaddrinfo(res);
    }

    int *fds = malloc((size_t)n_clients * sizeof(*fds));
    unsigned char *state = malloc((size_t)n_clients * sizeof(*state));
    if (!fds || !state) {
        fprintf(stderr, "allocation failed\n");
        free(fds);
        free(state);
        return 1;
    }

    for (int i = 0; i < n_clients; i++) {
        fds[i] = -1;
        state[i] = 0;
    }

    int ep = epoll_create1(0);
    if (ep < 0) {
        perror("epoll_create1");
        free(fds);
        free(state);
        return 1;
    }

    int established = 0;
    int failed = 0;
    int pending = 0;

    for (int i = 0; i < n_clients; i++) {
        int fd = socket(AF_INET, SOCK_STREAM, 0);
        if (fd < 0) {
            failed++;
            continue;
        }
        if (set_nonblocking_local(fd) < 0) {
            close(fd);
            failed++;
            continue;
        }

        int r = connect(fd, (struct sockaddr *)&sa, sizeof(sa));
        if (r == 0) {
            fds[i] = fd;
            state[i] = 1;
            established++;
            continue;
        }

        if (errno == EINPROGRESS || errno == EWOULDBLOCK || errno == EALREADY) {
            struct epoll_event ev;
            memset(&ev, 0, sizeof(ev));
            ev.events = EPOLLOUT | EPOLLERR | EPOLLHUP;
            ev.data.u32 = (uint32_t)i;

            if (epoll_ctl(ep, EPOLL_CTL_ADD, fd, &ev) < 0) {
                close(fd);
                failed++;
                continue;
            }

            fds[i] = fd;
            state[i] = 2;
            pending++;
            continue;
        }

        close(fd);
        failed++;
    }

    double deadline = now_seconds() + 30.0;
    struct epoll_event evs[256];

    while (pending > 0 && now_seconds() < deadline) {
        int n = epoll_wait(ep, evs, 256, 250);
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            break;
        }

        for (int k = 0; k < n; k++) {
            int idx = (int)evs[k].data.u32;
            if (idx < 0 || idx >= n_clients) {
                continue;
            }
            if (state[idx] != 2) {
                continue;
            }

            int fd = fds[idx];
            if (fd < 0) {
                state[idx] = 0;
                pending--;
                failed++;
                continue;
            }

            int soerr = 0;
            socklen_t slen = sizeof(soerr);
            if (getsockopt(fd, SOL_SOCKET, SO_ERROR, &soerr, &slen) < 0) {
                soerr = errno;
            }

            epoll_ctl(ep, EPOLL_CTL_DEL, fd, NULL);
            pending--;

            if (soerr == 0) {
                state[idx] = 1;
                established++;
            } else {
                close(fd);
                fds[idx] = -1;
                state[idx] = 0;
                failed++;
            }
        }
    }

    if (pending > 0) {
        for (int i = 0; i < n_clients; i++) {
            if (state[i] == 2) {
                if (fds[i] >= 0) {
                    epoll_ctl(ep, EPOLL_CTL_DEL, fds[i], NULL);
                    close(fds[i]);
                    fds[i] = -1;
                }
                state[i] = 0;
                pending--;
                failed++;
            }
        }
    }

    printf("clients_target=%d established=%d failed=%d\n", n_clients, established, failed);
    fflush(stdout);

    if (hold_seconds > 0) {
        struct timespec ts;
        ts.tv_sec = hold_seconds;
        ts.tv_nsec = 0;
        while (nanosleep(&ts, &ts) != 0 && errno == EINTR) {
        }
    }

    for (int i = 0; i < n_clients; i++) {
        if (state[i] == 1 && fds[i] >= 0) {
            close(fds[i]);
        }
    }

    close(ep);
    free(fds);
    free(state);
    return 0;
}
