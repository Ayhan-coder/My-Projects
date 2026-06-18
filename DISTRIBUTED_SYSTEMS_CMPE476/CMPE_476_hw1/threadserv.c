/* threadserv.c — YOUR implementation of Part A (thread-per-connection).
 *
 * See Section 7 of the project definition.
 * Usage:  ./threadserv [port]   (default port 9090)
 */
#include "server_api.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <signal.h>
#include <errno.h>
#include <arpa/inet.h>

static server_state_t g_state = {0, 0};
static pthread_mutex_t g_mutex = PTHREAD_MUTEX_INITIALIZER;

static void *worker(void *arg) {
    int fd = (int)(long)arg;
    char rbuf[4096];
    char line[MAX_LINE_LEN + 1];
    conn_buf_t buf;
    buffer_init(&buf);

    while (1) {
        ssize_t r = recv(fd, rbuf, sizeof(rbuf), 0);
        if (r <= 0) {
            break; /* EOF or error */
        }
        buffer_append(&buf, rbuf, (size_t)r);

        while (buffer_take_line(&buf, line, sizeof(line)) == 1) {
            if (line[0] == '\0') {
                /* line_too_long flag was surfaced */
                const char *err = "ERR line_too_long\n";
                send(fd, err, strlen(err), MSG_NOSIGNAL);
                goto done;
            }
            request_t req;
            if (parse_request(line, &req) == 0) {
                char resp[MAX_RESPONSE_LEN + 1];
                int n = format_response(&req, &g_state, resp, sizeof(resp));
                if (n >= 0) {
                    resp[n] = '\n';
                    resp[n + 1] = '\0';
                    send(fd, resp, n + 1, MSG_NOSIGNAL);
                }
                if (req.kind == CMD_QUIT) {
                    goto done;
                }
            }
        }
    }
done:
    close(fd);
    pthread_mutex_lock(&g_mutex);
    if (g_state.active_connections > 0) g_state.active_connections--;
    pthread_mutex_unlock(&g_mutex);
    return NULL;
}

int main(int argc, char **argv) {
    int port = (argc > 1) ? atoi(argv[1]) : 9090;
    signal(SIGPIPE, SIG_IGN);
    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        perror("socket");
        return 1;
    }
    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = INADDR_ANY;
    if (bind(listen_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(listen_fd);
        return 1;
    }
    if (listen(listen_fd, SOMAXCONN) < 0) {
        perror("listen");
        close(listen_fd);
        return 1;
    }
    printf("threadserv listening on port %d\n", port);
    while (1) {
        struct sockaddr_in cli = {0};
        socklen_t clilen = sizeof(cli);
        int client_fd = accept(listen_fd, (struct sockaddr*)&cli, &clilen);
        if (client_fd < 0) {
            if (errno == EINTR) continue;
            perror("accept");
            break;
        }
        pthread_mutex_lock(&g_mutex);
        g_state.active_connections++;
        g_state.total_connections++;
        pthread_mutex_unlock(&g_mutex);
        pthread_t tid;
        if (pthread_create(&tid, NULL, worker, (void*)(long)client_fd) != 0) {
            perror("pthread_create");
            close(client_fd);
            pthread_mutex_lock(&g_mutex);
            if (g_state.active_connections > 0) g_state.active_connections--;
            pthread_mutex_unlock(&g_mutex);
            continue;
        }
        pthread_detach(tid);
    }
    close(listen_fd);
    return 0;
}
