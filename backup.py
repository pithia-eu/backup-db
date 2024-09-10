import logging
import os
import scp
import paramiko
from datetime import datetime
from dotenv import load_dotenv


logging.basicConfig(filename='backup.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FILE_PATTERN_ALL = "~/esc_all_system_dbs_{timestamp}.{ext}"
FILE_PATTERN_DB = "~/esc_db_{timestamp}.{ext}"


def get_env_variable(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing environment variable '{name}'")
    return value


def create_ssh_client(ssh_host, ssh_port, ssh_user, ssh_key_path):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    client.connect(ssh_host, port=ssh_port, username=ssh_user, key_filename=ssh_key_path)
    logging.info('SSH Client created')
    return client


def generate_backup_files(timestamp):
    return [
        FILE_PATTERN_ALL.format(timestamp=timestamp, ext="sql"),
        FILE_PATTERN_DB.format(timestamp=timestamp, ext="sql"),
        FILE_PATTERN_DB.format(timestamp=timestamp, ext="tar")
    ]


def generate_backup_command(postgres_user, command, filename):
    return f'sudo su {postgres_user} -c "{command} {filename}"'


def generate_backup_commands(timestamp, postgres_user, dbname):
    backup_files = generate_backup_files(timestamp)
    commands = {
        "dumpall": f"pg_dumpall -U {postgres_user} -f",
        "dump": f"pg_dump -d {dbname} -f",
        "dump_tar": f"pg_dump -d {dbname}  -F tar"
    }

    return [
        generate_backup_command(postgres_user, commands['dumpall'], backup_files[0]),
        generate_backup_command(postgres_user, commands['dump'], backup_files[1]),
        generate_backup_command(postgres_user, commands['dump_tar'], backup_files[2])
    ]


def create_database_backups(ssh_client, timestamp, postgres_user, dbname):
    logging.info('Creating database backups')
    commands = generate_backup_commands(timestamp, postgres_user, dbname)
    for command in commands:
        logging.info(f'Creating database backup with command: {command}')
        ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(command)
        exit_status = ssh_stdout.channel.recv_exit_status()
        if exit_status != 0:
            logging.error(f'Creating database backup failed: {ssh_stderr.read()}')
        else:
            logging.info(f'Creating database backup completed: {ssh_stdout.read()}')


def download_database_backups(ssh_client, timestamp):
    logging.info('Collecting backup files')
    backup_files = generate_backup_files(timestamp)
    scp_client = scp.SCPClient(ssh_client.get_transport())
    for file in backup_files:
        logging.info(f'Collecting backup file: {file}')
        scp_client.get(file, local_path='.')
    scp_client.close()


def backup(timestamp):
    backup_ssh_host = get_env_variable("BACKUP_SSH_HOST")
    backup_ssh_port = int(get_env_variable("BACKUP_SSH_PORT"))
    backup_ssh_user = get_env_variable("BACKUP_SSH_USER")
    backup_ssh_key_path = get_env_variable("BACKUP_SSH_KEY_PATH")
    backup_postgres_user = get_env_variable("BACKUP_POSTGRES_USER")
    backup_dbname = get_env_variable("BACKUP_DBNAME")
    ssh_client = create_ssh_client(backup_ssh_host,
                                   backup_ssh_port,
                                   backup_ssh_user,
                                   backup_ssh_key_path)
    create_database_backups(ssh_client,
                            timestamp,
                            backup_postgres_user,
                            backup_dbname)
    download_database_backups(ssh_client, timestamp)
    ssh_client.close()


def restore():
    pass


def main():
    logging.info('Backup starts')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    load_dotenv()
    backup(timestamp)
    if get_env_variable("RESTORE"):
        restore()
    logging.info('Backup completed successfully')


if __name__ == '__main__':
    main()
