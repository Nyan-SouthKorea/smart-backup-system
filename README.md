
# Auto Backup Script

## Overview
The **Auto Backup Script** is a Python utility designed to automate file and directory backups. It is highly customizable, allowing users to exclude specific files, directories, and datasets based on defined criteria. The script does not rely on external progress bars like `tqdm`, ensuring simplicity and compatibility.

---

## Features
- **Customizable Exclusions**:
  - Skip dataset directories containing more than a specified number of files.
  - Exclude files exceeding a predefined size limit.
- **Path Normalization**:
  - Ensures consistent path handling across operating systems.
- **Backup Integrity**:
  - Logs excluded files and directories in JSON format.
- **Support for Long Paths**:
  - Uses UNC paths to manage long file paths exceeding Windows' default 260-character limit.
- **Efficiency**:
  - Provides intermediate progress updates during large backups.

---

## Requirements
- **Python 3.6** or later
- No additional dependencies are required.

---

## Installation
Clone or download this repository to your local machine.

---

## Usage

### Initialization
The script can be used by creating an instance of the `Auto_backup` class with the following parameters:
- `source_path`: The directory to back up.
- `backup_path`: The destination directory for the backup.
- `dataset_limit_counter`: The maximum number of dataset files allowed in a folder before exclusion.
- `limit_file_size_gb`: The maximum allowable file size in gigabytes. Files exceeding this limit will be excluded.

### Example Usage
```python
from auto_backup import Auto_backup

source_path = 'Z:/data2/iena'
backup_path = 'C:/1. GPU 서버 백업'
dataset_limit_counter = 50
limit_file_size_gb = 0.2

Auto_backup(source_path, backup_path, dataset_limit_counter, limit_file_size_gb).auto_backup()
```

---

## Class and Method Details

### **`Auto_backup`**
#### **`__init__(self, source_path, backup_path, dataset_limit_counter, limit_file_size_gb)`**
Initializes the backup configuration.
- **`source_path`**: Source directory for the backup.
- **`backup_path`**: Destination directory for the backup.
- **`dataset_limit_counter`**: Threshold for dataset folder exclusion.
- **`limit_file_size_gb`**: Maximum file size to include in the backup.

#### **`path_nor(self, path)`**
Normalizes the provided path:
- Replaces `\` with `/`.
- Ensures consistent separators.

#### **`sourcepath_to_backuppath(self, root)`**
Converts a source directory path to the corresponding backup directory path.

#### **`is_dataset(self, path)`**
Checks if a directory qualifies as a dataset and excludes it from the backup.

#### **`is_file_big(self, path)`**
Determines if a file exceeds the maximum size limit and excludes it if necessary.

#### **`make_json(self, path, data)`**
Writes data to a JSON file at the specified path.

#### **`makedirs_long(self, path)`**
Creates directories using UNC path handling for long paths.

#### **`make_folders_and_count(self)`**
Creates the folder structure in the backup path and counts the total number of directories.

#### **`auto_backup(self)`**
Performs the complete backup process:
1. Creates necessary directories.
2. Copies files while applying exclusions.
3. Logs skipped or excluded items.

#### **`save_log(self)`**
Generates JSON logs for:
- Skipped large files.
- Dataset folders.
- Errors encountered during the backup.

---

## Logs
The script generates the following log files:
1. **`big_file_list.json`**: Details of files excluded due to size.
2. **`is_file_big_error_list.json`**: Errors encountered while processing file sizes.
3. **`dataset_folder_list.json`**: List of dataset folders excluded.
4. **`is_dataset_error_list.json`**: Errors encountered while checking for datasets.
5. **`auto_backup_error_list.json`**: Errors encountered during the backup process.

Logs are stored under the `log/` directory within the backup path.

---

## Example Output
During execution, the script provides real-time updates:
```
폴더 생성 중...
folders 10ea created...
폴더 생성 50개 완료! 자동 백업 시작...
completed: 100/150
백업 완료!
```

---

## Notes
1. Ensure the source and backup paths are accessible.
2. Use UNC paths (`\\?\`) for long paths on Windows.
3. Customize `self.pass_dirs` to exclude additional directories if needed.
4. Files with extensions in `self.must_copy` will always be backed up, even if they exceed size limits.

---

## License
This project is licensed under the MIT License.

---

For further questions or contributions, feel free to open an issue or submit a pull request.
