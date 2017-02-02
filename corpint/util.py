

def ensure_column(table, name, type):
    if name not in table.columns:
        table.create_column(name, type)
