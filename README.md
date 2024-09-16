# backup-db

## PostgreSQL Database Backup and Restore Python project

## Introduction

This project is a database backup and restore system designed to automate the backup/restore process.

This system is capable of:

- Backing up a PostgreSQL database to a remote SSH host.
- Restoring the database from a backup available on the remote SSH host.

## Configuration

To configure this system to match your database and remote host, you must define several environment variables in the `.env` file:

### Backup Configuration

- `BACKUP_SSH_KEY_PATH`: Path to your private SSH key for the backup host.
- `BACKUP_SSH_HOST`: SSH hostname or IP address for the backup host.
- `BACKUP_SSH_PORT`: SSH port number for the backup host.
- `BACKUP_SSH_USER`: SSH username for the backup host.
- `BACKUP_POSTGRES_USER`: PostgreSQL username for the database to be backed up.
- `BACKUP_DBNAME`: Name of the PostgreSQL database to be backed up.
- `BACKUP_SSH_PATH`: The backup host's path where the backup will be stored.
- `BACKUP_TO_PATH`: The local host's path where the backup will be stored.

### Restore Configuration

- `RESTORE_SSH_KEY_PATH`: Path to your private SSH key for the restore host.
- `RESTORE_SSH_HOST`: SSH hostname or IP address for the restore host.
- `RESTORE_SSH_PORT`: SSH port number for the restore host.
- `RESTORE_SSH_USER`: SSH username for the restore host.
- `RESTORE_POSTGRES_USER`: PostgreSQL username for the database to be restored.
- `RESTORE_SSH_PATH`: The restore host's path where the backup will be retrieved.
- `RESTORE`: Set to `True` to enable the restoration process. Otherwise, set to `False`.

## Getting Started

To properly set up the environment and run the backup and restore processes, follow these steps:

1. Ensure that the host running the script can establish an SSH connection to both the backup and the restore hosts.
2. Set up your SSH keys and make sure they are configured correctly on both the backup and restore hosts.
3. Install `acl` on both the backup and restore hosts. This is necessary as the script sets file permissions on the remote hosts for `BACKUP_SSH_PATH` and `RESTORE_SSH_PATH`, respectively. You can install `acl` using the following command: `sudo apt install acl`
4. Set up the python environment by running the command "./bin/setup_venv" at the project root folder.
5. Set  up the cronjob by running the command "./bin/setup_cron" at the project root folder.

By doing so the deployment is ready and runs at midnight every day.

## Manual Run

To run the program manual you must complete steps 1-4 as described above. 

There are two options to run the program:

1. At the project root directory execute the command: './bin/back_db.sh' to run the script that initiates the program.
2. At the project root directory execute the command: 'python3 main.py' to run directly the python code.

## Testing and Logs

The program offers a test option where no backup and restore happens. It only tests ssh connectivity, file creation/permissions.

To initiate a test run at the project root directory execute the command: 'python3 main.py --test'.

Logs can be found at the project directory in the log folder. Log file back_db.log is for the cron job and log file main.log comes from the python code itself.
