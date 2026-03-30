#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sqlite3.h>

#define ID_RANDOM_LENGTH 8

typedef struct {
    char id[32];
    char event[1024];
    char created_at[32];
} AuditRecord;

static void generate_random_string(char *dest, size_t length) {
    const char charset[] = "abcdefghijklmnopqrstuvwxyz0123456789";
    for (size_t i = 0; i < length; i++) {
        int key = rand() % (int)(sizeof(charset) - 1);
        dest[i] = charset[key];
    }
    dest[length] = '\0';
}

static void generate_iso_timestamp(char *buffer, size_t size) {
    time_t now = time(NULL);
    struct tm *tm_info = gmtime(&now);
    strftime(buffer, size, "%Y-%m-%dT%H:%M:%SZ", tm_info);
}

static int ensure_table_exists(sqlite3 *db) {
    const char *sql =
        "CREATE TABLE IF NOT EXISTS audit_log ("
        "id TEXT PRIMARY KEY,"
        "event TEXT NOT NULL,"
        "created_at TEXT NOT NULL"
        ");";
    char *errmsg = NULL;
    int rc = sqlite3_exec(db, sql, NULL, NULL, &errmsg);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Failed to ensure table: %s\n", errmsg ? errmsg : "unknown");
        sqlite3_free(errmsg);
        return -1;
    }
    return 0;
}

static int write_audit_event(sqlite3 *db, const char *message, AuditRecord *out) {
    if (!db || !message || !out) return -1;

    AuditRecord record;
    char random_part[ID_RANDOM_LENGTH + 1];
    generate_random_string(random_part, ID_RANDOM_LENGTH);
    snprintf(record.id, sizeof(record.id), "audit_%s", random_part);

    snprintf(record.event, sizeof(record.event), "%s", message);

    generate_iso_timestamp(record.created_at, sizeof(record.created_at));

    const char *sql =
        "INSERT INTO audit_log (id, event, created_at) VALUES (?, ?, ?);";

    sqlite3_stmt *stmt = NULL;
    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Prepare failed: %s\n", sqlite3_errmsg(db));
        return -1;
    }

    sqlite3_bind_text(stmt, 1, record.id, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, record.event, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 3, record.created_at, -1, SQLITE_STATIC);

    rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    if (rc != SQLITE_DONE) {
        fprintf(stderr, "Insert failed: %s\n", sqlite3_errmsg(db));
        return -1;
    }

    *out = record;
    return 0;
}

static void print_json_escaped(const char *s) {
    for (const unsigned char *p = (const unsigned char *)s; *p; p++) {
        unsigned char c = *p;
        if (c == '\\' || c == '"') {
            fputc('\\', stdout);
            fputc(c, stdout);
        } else if (c == '\n') {
            fputs("\\n", stdout);
        } else if (c == '\r') {
            fputs("\\r", stdout);
        } else if (c == '\t') {
            fputs("\\t", stdout);
        } else if (c < 0x20) {
            printf("\\u%04x", c);
        } else {
            fputc(c, stdout);
        }
    }
}

int main(int argc, char **argv) {
    const char *db_path = NULL;
    const char *event = NULL;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--db") == 0 && i + 1 < argc) {
            db_path = argv[++i];
        } else if (strcmp(argv[i], "--event") == 0 && i + 1 < argc) {
            event = argv[++i];
        }
    }

    if (!db_path || !event) {
        fprintf(stderr, "Usage: %s --db <path> --event <message>\n", argv[0]);
        return 2;
    }

    srand((unsigned int)time(NULL));

    sqlite3 *db = NULL;
    if (sqlite3_open(db_path, &db) != SQLITE_OK) {
        fprintf(stderr, "Cannot open db: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return 3;
    }

    if (ensure_table_exists(db) != 0) {
        sqlite3_close(db);
        return 4;
    }

    AuditRecord rec;
    if (write_audit_event(db, event, &rec) != 0) {
        sqlite3_close(db);
        return 5;
    }

    sqlite3_close(db);

    fputs("{\"id\":\"", stdout); print_json_escaped(rec.id);
    fputs("\",\"event\":\"", stdout); print_json_escaped(rec.event);
    fputs("\",\"createdAt\":\"", stdout); print_json_escaped(rec.created_at);
    fputs("\"}\n", stdout);

    return 0;
}
