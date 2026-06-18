/* epollserv.c — YOUR implementation of Part B (epoll event loop).
 *
 * See Section 8 of the project definition.
 * Usage:  ./epollserv [port]   (default port 9091)
 */
#include "server_api.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/epoll.h>
#include <signal.h>
#include <errno.h>
#include <fcntl.h>

#define MAX_EVENTS 256
#define INTEST 1

typedef struct {
    int fd;
    conn_buf_t buf;
} client_t;

static server_state_t g_state = {0, 0};
static int g_listen_fd = -1;
static int g_epoll_fd = -1;

static void close_client(client_t *c) {
    if (!c || c->fd < 0) return;
    epoll_ctl(g_epoll_fd, EPOLL_CTL_DEL, c->fd, NULL);
    close(c->fd);
    c->fd = -1;
    if (g_state.active_connections > 0) g_state.active_connections--;
    free(c);
}

static void handle_client(client_t *c) {
    if (!c || c->fd < 0) return;
    char tmp[4096];
    for (;;) {
        ssize_t r = recv(c->fd, tmp, sizeof tmp, 0);
        if (r < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) break;
            close_client(c);
            return;
        }
        if (r == 0) {
            close_client(c);
            return;
        }
        buffer_append(&c->buf, tmp, r);
        char line[MAX_LINE_LEN + 1];
        int was_too_long = c->buf.line_too_long;
        while (buffer_take_line(&c->buf, line, sizeof line) == 1) {
            if (was_too_long) {
                /* line_too_long flag was latched; take_line cleared it */
                const char *err = "ERR line_too_long\n";
                send(c->fd, err, strlen(err), MSG_NOSIGNAL);
                close_client(c);
                return;
            }
            request_t req;
            if (parse_request(line, &req) == 0) {
                char resp[MAX_RESPONSE_LEN + 1];
                int n = format_response(&req, &g_state, resp, sizeof(resp));
                if (n >= 0) {
                    resp[n] = '\n';
                    resp[n + 1] = '\0';
                    ssize_t s = send(c->fd, resp, n + 1, MSG_NOSIGNAL);
                    if (s < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
                        close_client(c);
                        return;
                    }
                }
                if (req.kind == CMD_QUIT) {
                    close_client(c);
                    return;
                }
            }
            was_too_long = c->buf.line_too_long;
        }
    }
}

static void handle_accept() {
    for (;;) {
        struct sockaddr_in cli = {0};
        socklen_t clilen = sizeof(cli);
        int client_fd = accept(g_listen_fd, (struct sockaddr*)&cli, &clilen);
        if (client_fd < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) break;
            if (errno == EINTR) continue;
            perror("accept");
            break;
        }
        set_nonblocking(client_fd);
        client_t *c = malloc(sizeof(client_t));
        if (!c) {
            close(client_fd);
            continue;
        }
        c->fd = client_fd;
        buffer_init(&c->buf);
        struct epoll_event ev = {0};
        ev.events = EPOLLIN | EPOLLET;
        ev.data.ptr = c;
        if (epoll_ctl(g_epoll_fd, EPOLL_CTL_ADD, client_fd, &ev) < 0) {
            perror("epoll_ctl add");
            free(c);
            close(client_fd);
            continue;
        }
        g_state.active_connections++;
        g_state.total_connections++;
    }
}

int main(int argc, char **argv) {
    int port = (argc > 1) ? atoi(argv[1]) : 9091;
    signal(SIGPIPE, SIG_IGN);
    g_listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (g_listen_fd < 0) {
        perror("socket");
        return 1;
    }
    set_nonblocking(g_listen_fd);
    int opt = 1;
    setsockopt(g_listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = INADDR_ANY;
    if (bind(g_listen_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(g_listen_fd);
        return 1;
    }
    if (listen(g_listen_fd, SOMAXCONN) < 0) {
        perror("listen");
        close(g_listen_fd);
        return 1;
    }
    g_epoll_fd = epoll_create1(0);
    if (g_epoll_fd < 0) {
        perror("epoll_create1");
        close(g_listen_fd);
        return 1;
    }
    struct epoll_event ev = {0};
    ev.events = EPOLLIN | EPOLLET;
    ev.data.ptr = NULL;  /* special for listen fd */
    if (epoll_ctl(g_epoll_fd, EPOLL_CTL_ADD, g_listen_fd, &ev) < 0) {
        perror("epoll_ctl listen");
        close(g_listen_fd);
        close(g_epoll_fd);
        return 1;
    }
    printf("epollserv listening on port %d\n", port);
    struct epoll_event events[MAX_EVENTS];
    while (1) {
        int n = epoll_wait(g_epoll_fd, events, MAX_EVENTS, -1);
        if (n < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait");
            break;
        }
        for (int i = 0; i < n; i++) {
            if (events[i].data.ptr == NULL) {
                handle_accept();
            } else {
                client_t *c = (client_t *)events[i].data.ptr;
                if (c && c->fd >= 0) {
                    if (events[i].events & (EPOLLIN | EPOLLERR | EPOLLHUP)) {
                        handle_client(c);
                    }
                }
            }
        }
    }
    close(g_listen_fd);
    close(g_epoll_fd);
    return 0;
}
