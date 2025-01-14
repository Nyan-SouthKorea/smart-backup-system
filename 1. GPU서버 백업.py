from auto_backup import Auto_backup

source_path = 'Z:/data2/iena'
backup_path = 'C:/1. GPU 서버 백업'
dataset_limit_counter = 100
limit_file_size_gb = 3
Auto_backup(source_path, backup_path, dataset_limit_counter, limit_file_size_gb).auto_backup()