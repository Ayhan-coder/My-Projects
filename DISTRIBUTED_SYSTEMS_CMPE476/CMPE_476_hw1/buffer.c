/* buffer.c — YOUR implementation goes here.
 * See server_api.h for the exact signatures and required behaviour.
 */
#include "server_api.h"
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

int set_nonblocking(int fd) {
    int fl = fcntl(fd, F_GETFL, 0);
    if (fl < 0) return -1;
    return fcntl(fd, F_SETFL, fl | O_NONBLOCK);
}

void buffer_init(conn_buf_t *b) {
    if (!b) return;
    b->len = 0;
    b->line_too_long = 0;
}

int buffer_append(conn_buf_t *b, const char *data, size_t n) {
    if (!b || !data) return -1;
    if (n == 0) return 0;
    if (b->len + n > CONN_BUF_CAPACITY) {
        int has_nl = 0;
        for (size_t i = 0; i < b->len && !has_nl; i++) {
            if (b->data[i] == '\n') has_nl = 1;
        }
        if (!has_nl) {
            for (size_t i = 0; i < n && !has_nl; i++) {
                if (data[i] == '\n') has_nl = 1;
            }
        }
        if (!has_nl) {
            b->len = 0;
            b->line_too_long = 1;
            return 0;
        }
        /* has \n somewhere, append what fits; remainder will arrive
           on the next recv after the caller drains complete lines */
        size_t can = CONN_BUF_CAPACITY - b->len;
        if (can > n) can = n;
        if (can > 0) {
            memcpy(b->data + b->len, data, can);
            b->len += can;
        }
        return 0;
    }
    /* normal append */
    memcpy(b->data + b->len, data, n);
    b->len += n;
    return 0;
}

int buffer_take_line(conn_buf_t *b, char *out, size_t outmax) {
    if (!b || !out || outmax == 0) return -1;
    if (b->line_too_long) {
        out[0] = '\0';
        b->line_too_long = 0;
        return 1;
    }
    for (size_t i = 0; i < b->len; i++) {
        if (b->data[i] == '\n') {
            size_t linelen = i;
            if (linelen > 0 && b->data[linelen - 1] == '\r') linelen--;
            size_t copy = (linelen < outmax - 1) ? linelen : outmax - 1;
            memcpy(out, b->data, copy);
            out[copy] = '\0';
            size_t rest = b->len - (i + 1);
            if (rest > 0) {
                memmove(b->data, b->data + i + 1, rest);
            }
            b->len = rest;
            return 1;
        }
    }
    return 0;
}
