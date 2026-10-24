from db import execute_query

def fix_table(table, fk_index_name):
    print("-- Fixing " + table + " --")
    fks = execute_query(
        "SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE "
        "WHERE TABLE_NAME=%s AND TABLE_SCHEMA=DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL",
        (table,), fetch_all=True
    ) or []
    print("  FKs: " + str([f['CONSTRAINT_NAME'] for f in fks]))

    for fk in fks:
        name = fk['CONSTRAINT_NAME']
        try:
            execute_query("ALTER TABLE " + table + " DROP FOREIGN KEY `" + name + "`", commit=True)
            print("  Dropped FK: " + name)
        except Exception as e:
            print("  Skip FK " + name + ": " + str(e))

    try:
        execute_query("ALTER TABLE " + table + " DROP INDEX `" + fk_index_name + "`", commit=True)
        print("  Dropped UNIQUE index: " + fk_index_name)
    except Exception as e:
        print("  Skip UNIQUE drop: " + str(e))

    try:
        execute_query("ALTER TABLE " + table + " ADD INDEX idx_" + table + "_uid (user_id)", commit=True)
        print("  Added plain index on user_id")
    except Exception as e:
        print("  Skip add index: " + str(e))

# Fix provincial_admins
fix_table('provincial_admins', 'user_id')
try:
    execute_query("ALTER TABLE provincial_admins ADD CONSTRAINT fk_pa_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE", commit=True)
    print("  FK user ok")
except Exception as e:
    print("  FK user: " + str(e))
try:
    execute_query("ALTER TABLE provincial_admins ADD CONSTRAINT fk_pa_prov FOREIGN KEY (province_id) REFERENCES provinces(id) ON DELETE CASCADE", commit=True)
    print("  FK province ok")
except Exception as e:
    print("  FK province: " + str(e))

# Fix municipality_admins
fix_table('municipality_admins', 'user_id')
try:
    execute_query("ALTER TABLE municipality_admins ADD CONSTRAINT fk_ma_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE", commit=True)
    print("  FK user ok")
except Exception as e:
    print("  FK user: " + str(e))
try:
    execute_query("ALTER TABLE municipality_admins ADD CONSTRAINT fk_ma_muni FOREIGN KEY (municipality_id) REFERENCES municipalities(id) ON DELETE CASCADE", commit=True)
    print("  FK municipality ok")
except Exception as e:
    print("  FK municipality: " + str(e))

print("Done.")
