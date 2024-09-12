import scp

from source.log.logger import logger
from source.utils.environment import get_env_variable
from source.utils.ssh import create_ssh_client

FILE_PATTERN_ALL = "{backup_ssh_path}/{backup_dbname}_all_system_dbs_{timestamp}.{ext}"
FILE_PATTERN_DB = "{backup_ssh_path}/{backup_dbname}_db_{timestamp}.{ext}"


def generate_backup_file_paths(timestamp,
                               backup_dbname,
                               backup_ssh_path):
    return [
        FILE_PATTERN_ALL.format(backup_ssh_path=backup_ssh_path,
                                backup_dbname=backup_dbname,
                                timestamp=timestamp,
                                ext="sql"),
        FILE_PATTERN_DB.format(backup_ssh_path=backup_ssh_path,
                               backup_dbname=backup_dbname,
                               timestamp=timestamp,
                               ext="sql"),
        FILE_PATTERN_DB.format(backup_ssh_path=backup_ssh_path,
                               backup_dbname=backup_dbname,
                               timestamp=timestamp,
                               ext="tar")
    ]


def generate_backup_command(postgres_user,
                            command,
                            filename):
    return f'sudo su {postgres_user} -c "{command} {filename}"'


def generate_backup_commands(timestamp,
                             postgres_user,
                             backup_dbname,
                             backup_ssh_path):
    backup_files = generate_backup_file_paths(timestamp,
                                              backup_dbname,
                                              backup_ssh_path)
    commands = {
        "dumpall": f"pg_dumpall -U {postgres_user} -f",
        "dump": f"pg_dump -d {backup_dbname} -f",
        "dump_tar": f"pg_dump -d {backup_dbname}  -F tar"
    }

    return [
        generate_backup_command(postgres_user,
                                commands['dumpall'],
                                backup_files[0]),
        generate_backup_command(postgres_user,
                                commands['dump'],
                                backup_files[1]),
        generate_backup_command(postgres_user,
                                commands['dump_tar'],
                                backup_files[2])
    ]


def create_database_backups(ssh_client,
                            timestamp,
                            postgres_user,
                            backup_dbname,
                            backup_ssh_path,
                            test=False):
    if test:
        logger.warning('Test model enabled - backup disabled')
    else:
        logger.info('Creating database backups')
    commands = generate_backup_commands(timestamp,
                                        postgres_user,
                                        backup_dbname,
                                        backup_ssh_path)
    for command in commands:
        logger.debug(f'Command: {command}')
        if not test:
            logger.info(f'Creating database backup with command: {command}')
            ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(command)
            exit_status = ssh_stdout.channel.recv_exit_status()
            if exit_status != 0:
                logger.error(f'Creating database backup failed: {ssh_stderr.read()}')
            else:
                logger.info(f'Creating database backup completed: {ssh_stdout.read()}')


def download_database_backups(ssh_client,
                              timestamp,
                              backup_dbname,
                              backup_ssh_path,
                              backup_to_path,
                              test=False):
    if test:
        logger.warning('Test model enabled - collecting backup files disabled')
    else:
        logger.info('Collecting database backups')
    backup_files = generate_backup_file_paths(timestamp,
                                              backup_dbname,
                                              backup_ssh_path)
    scp_client = scp.SCPClient(ssh_client.get_transport())
    for file in backup_files:
        logger.debug(f'file: {file} to: {backup_to_path}')
        if not test:
            logger.info(f'Collecting..')
            scp_client.get(file,
                           local_path=backup_to_path)
            logger.info(f'Collected')
    scp_client.close()


def backup(timestamp,
           test=False):
    logger.info('Backing up Postgres Server..')
    backup_ssh_key_path = get_env_variable("BACKUP_SSH_KEY_PATH")
    backup_ssh_host = get_env_variable("BACKUP_SSH_HOST")
    backup_ssh_port = int(get_env_variable("BACKUP_SSH_PORT"))
    backup_ssh_user = get_env_variable("BACKUP_SSH_USER")
    backup_postgres_user = get_env_variable("BACKUP_POSTGRES_USER")
    backup_dbname = get_env_variable("BACKUP_DBNAME")
    backup_ssh_path = get_env_variable("BACKUP_SSH_PATH")
    backup_to_path = get_env_variable("BACKUP_TO_PATH")
    backup_ssh_client = create_ssh_client(backup_ssh_host,
                                          backup_ssh_port,
                                          backup_ssh_user,
                                          backup_ssh_key_path)
    create_database_backups(backup_ssh_client,
                            timestamp,
                            backup_postgres_user,
                            backup_dbname,
                            backup_ssh_path,
                            test)

    download_database_backups(backup_ssh_client,
                              timestamp,
                              backup_dbname,
                              backup_ssh_path,
                              backup_to_path,
                              test)
    backup_ssh_client.close()
    logger.info('Backing up Postgres Server completed')
