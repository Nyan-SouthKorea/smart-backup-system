from auto_backup import Auto_backup

source_path = 'D:'
backup_path = 'C:/2. D드라이브 백업'
dataset_limit_counter = 100
limit_file_size_gb = 3
Auto_backup(source_path, backup_path, dataset_limit_counter, limit_file_size_gb).auto_backup()