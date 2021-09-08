import json
from apollo.connections import postgres
from apollo.utils import var_to_dict

def flatten_freshness_details(run_id: int, step: int, table: str, data: dict) -> dict:
    d = {
        "run_id": run_id,
        "step": step,
        "table_name": table.split('.')[-1],
        "max_loaded_at": data['max_loaded_at'],
        "snapshotted_at": data['snapshotted_at'],
        "seconds_since_refresh": data['max_loaded_at_time_ago_in_s'],
        "fresh_state": data['state'],
        "error_after": f"{data['criteria']['error_after']['count']} {data['criteria']['error_after']['period']}"
    }
    return d

def freshness_details(run_id: int, step: int) -> list:
    pg = postgres()    
    with open('sources.json') as f:
        data = json.load(f)
    generated_at = data['meta']['generated_at']
    elapsed_time = data['meta']['elapsed_time']
    sources = data['sources']
    total_error, total_pass = 0, 0
    failed_tables = []
    tables = ','.join([table.split('.')[-1] for table in sources.keys()])
    for table in sources.keys():
        if sources[table]['state'] == 'error':
            total_error += 1
            failed_tables.append(table.split('.')[-1])
        else:
            total_pass += 1
        freshness_details = flatten_freshness_details(run_id, step, table, sources[table])
        pg.dict_to_table(freshness_details, 'freshness_detailed')
    failed_tables_str = ','.join(failed_tables)
    freshness = var_to_dict(run_id=run_id, step=step, tables=tables,
                            failed_tables=failed_tables_str, total_pass=total_pass,
                            total_error=total_error, generated_at=generated_at, 
                            elapsed_time=elapsed_time)
    pg.dict_to_table(freshness, 'freshness')
    pg.close()
    return failed_tables