/* protocol.c — YOUR implementation goes here.
 * See server_api.h for the exact signatures and required behaviour.
 * See the project definition (CMPE476-C10K-Project.docx, Section 6) for
 * the semantics of each command.
 */
#include "server_api.h"
#include <string.h>
#include <stdio.h>
#include <time.h>
#include <inttypes.h>

int parse_request(const char *line, request_t *out) {
    if (!line || !out) return -1;
    out->arg[0] = '\0';
    if (line[0] == '\0' || line[0] == ' ' || line[0] == '\t') {
        out->kind = CMD_UNKNOWN;
        return 0;
    }
    const char *space = strchr(line, ' ');
    char cmd[32] = {0};
    if (space) {
        size_t clen = space - line;
        if (clen > sizeof(cmd) - 1) clen = sizeof(cmd) - 1;
        memcpy(cmd, line, clen);
        cmd[clen] = '\0';
        const char *argstart = space + 1;
        size_t alen = strlen(argstart);
        if (alen > MAX_LINE_LEN) alen = MAX_LINE_LEN;
        memcpy(out->arg, argstart, alen);
        out->arg[alen] = '\0';
    } else {
        size_t clen = strlen(line);
        if (clen > sizeof(cmd) - 1) clen = sizeof(cmd) - 1;
        memcpy(cmd, line, clen);
        cmd[clen] = '\0';
    }
    if (strcmp(cmd, "PING") == 0) {
        out->kind = CMD_PING;
        out->arg[0] = '\0';
    } else if (strcmp(cmd, "TIME") == 0) {
        out->kind = CMD_TIME;
        out->arg[0] = '\0';
    } else if (strcmp(cmd, "STATS") == 0) {
        out->kind = CMD_STATS;
        out->arg[0] = '\0';
    } else if (strcmp(cmd, "QUIT") == 0) {
        out->kind = CMD_QUIT;
        out->arg[0] = '\0';
    } else if (strcmp(cmd, "ECHO") == 0) {
        out->kind = CMD_ECHO;
        /* arg already set, or remains "" if no space */
    } else {
        out->kind = CMD_UNKNOWN;
        out->arg[0] = '\0';
    }
    return 0;
}

int format_response(const request_t *req, const server_state_t *st,
                    char *out, size_t outlen) {
    if (!req || !st || !out || outlen == 0) return -1;
    int n = 0;
    switch (req->kind) {
    case CMD_PING:
        n = snprintf(out, outlen, "PONG");
        break;
    case CMD_ECHO:
        n = snprintf(out, outlen, "%s", req->arg);
        break;
    case CMD_TIME: {
        time_t t = time(NULL);
        n = snprintf(out, outlen, "%" PRIu64, (uint64_t)t);
        break;
    }
    case CMD_STATS:
        n = snprintf(out, outlen, "%d", st->active_connections);
        break;
    case CMD_QUIT:
        n = snprintf(out, outlen, "BYE");
        break;
    case CMD_UNKNOWN:
        n = snprintf(out, outlen, "ERR unknown_command");
        break;
    case CMD_TOO_LONG:
        n = snprintf(out, outlen, "ERR line_too_long");
        break;
    default:
        n = snprintf(out, outlen, "ERR unknown_command");
        break;
    }
    if (n < 0) return -1;
    if ((size_t)n >= outlen) return (int)(outlen - 1);
    return n;
}
