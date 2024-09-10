import logging
import paramiko
import scp
from datetime import datetime
from dotenv import load_dotenv
import os

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FILE_PATTERN_ALL = "~/esc_all_system_dbs_{timestamp}.{ext}"
FILE_PATTERN_DB = "~/esc_db_{timestamp}.{ext}"


def create_ssh_client(hostname, port, username, key_filename):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port=port, username=username, key_filename=key_filename)
    logging.info('SSH Client created')
    return client


def generate_backup_files(timestamp):
    return [
        FILE_PATTERN_ALL.format(timestamp=timestamp, ext="sql"),
        FILE_PATTERN_DB.format(timestamp=timestamp, ext="sql"),
        FILE_PATTERN_DB.format(timestamp=timestamp, ext="tar")
    ]


def generate_backup_commands(timestamp):
    backup_files = generate_backup_files(timestamp)
    return [
        f'sudo su postgres -c "pg_dumpall -U postgres -f {backup_files[0]}"',
        f'sudo su postgres -c "pg_dump -d esc -f {backup_files[1]}"',
        f'sudo su postgres -c "pg_dump -d esc -F tar -f {backup_files[2]}"'
    ]


def create_database_backups(ssh_client, timestamp):
    logging.info('Creating database backups')
    commands = generate_backup_commands(timestamp)
    for command in commands:
        logging.info(f'Creating database backup with command: {command}')
        ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(command)
        if ssh_stderr:
            logging.error(f'Creating database backup failed: {ssh_stderr.read()}')
        else:
            logging.error(f'Creating database backup completed: {ssh_stdout.read()}')

def download_database_backups(ssh_client, timestamp):
    logging.info('Collecting backup files')
    backup_files = generate_backup_files(timestamp)
    scp_client = scp.SCPClient(ssh_client.get_transport())
    for file in backup_files:
        logging.info(f'Collecting backup file: {file}')
        scp_client.get(file, local_path='.')
    scp_client.close()


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    load_dotenv()
    ssh_host = os.getenv("SSH_HOST")
    ssh_port = int(os.getenv("SSH_PORT"))
    ssh_user = os.getenv("SSH_USER")
    ssh_key_path = os.getenv("SSH_KEY_PATH")
    ssh_client = create_ssh_client(ssh_host, ssh_port, ssh_user, ssh_key_path)
    create_database_backups(ssh_client, timestamp)
    download_database_backups(ssh_client, timestamp)
    ssh_client.close()


if __name__ == '__main__':
    logging.info('Backup starts')
    main()
    logging.info('Backup completed successfully')
