import scp
from source.log.logger import logger
from source.utils.environment import get_env_variable
from source.utils.ssh import create_ssh_client
from source.utils.directory import (create_ssh_directory,
                                    create_local_directory)
from source.utils.permissions import (change_ssh_directory_permissions,
                                      change_local_directory_permission)

BACKUP_FILE_PATTERN_ALL = "{backup_ssh_path}/{backup_dbname}_all_system_dbs_{timestamp}.{ext}"
BACKUP_FILE_PATTERN_DB = "{backup_ssh_path}/{backup_dbname}_db_{timestamp}.{ext}"


def generate_backup_file_paths(timestamp,
                               backup_dbname,
                               backup_ssh_path):
    return [
        BACKUP_FILE_PATTERN_ALL.format(backup_ssh_path=backup_ssh_path,
                                       backup_dbname=backup_dbname,
                                       timestamp=timestamp,
                                       ext="sql"),
        BACKUP_FILE_PATTERN_DB.format(backup_ssh_path=backup_ssh_path,
                                      backup_dbname=backup_dbname,
                                      timestamp=timestamp,
                                      ext="sql"),
        BACKUP_FILE_PATTERN_DB.format(backup_ssh_path=backup_ssh_path,
                                      backup_dbname=backup_dbname,
                                      timestamp=timestamp,
                                      ext="tar")
    ]


def generate_backup_command(backup_postgres_user,
                            backup_command,
                            backup_ssh_path):
    return f'sudo su {backup_postgres_user} -c "{backup_command} {backup_ssh_path}"'


def generate_backup_commands(timestamp,
                             backup_postgres_user,
                             backup_dbname,
                             backup_ssh_path):
    backup_files = generate_backup_file_paths(timestamp,
                                              backup_dbname,
                                              backup_ssh_path)
    backup_commands = {
        "dumpall": f"pg_dumpall -U {backup_postgres_user} -f",
        "dump": f"pg_dump -d {backup_dbname} -f",
        "dump_tar": f"pg_dump -d {backup_dbname} -F tar -f"
    }

    return [
        generate_backup_command(backup_postgres_user,
                                backup_commands['dumpall'],
                                backup_files[0]),
        generate_backup_command(backup_postgres_user,
                                backup_commands['dump'],
                                backup_files[1]),
        generate_backup_command(backup_postgres_user,
                                backup_commands['dump_tar'],
                                backup_files[2])
    ]


def create_database_backups(backup_ssh_client,
                            timestamp,
                            backup_postgres_user,
                            backup_dbname,
                            backup_ssh_path,
                            test=False):
    if test:
        logger.warning('Test model enabled - backup disabled')
    else:
        logger.info('Creating database backups')
    create_ssh_directory(backup_ssh_client,
                         backup_ssh_path)
    change_ssh_directory_permissions(backup_ssh_client,
                                     backup_postgres_user,
                                     backup_ssh_path)
    commands = generate_backup_commands(timestamp,
                                        backup_postgres_user,
                                        backup_dbname,
                                        backup_ssh_path)
    for command in commands:
        logger.debug(f'Command: {command}')
        if not test:
            logger.info(f'Creating database backup with command: {command}')
            ssh_stdin, ssh_stdout, ssh_stderr = backup_ssh_client.exec_command(command)
            exit_status = ssh_stdout.channel.recv_exit_status()
            if exit_status != 0:
                logger.error(f'Creating database backup failed: {ssh_stderr.read()}')
                raise Exception(f'Creating database backup failed: {ssh_stderr.read()}')
            else:
                logger.info(f'Creating database backup completed: {ssh_stdout.read()}')


def download_database_backups(backup_ssh_client,
                              timestamp,
                              backup_dbname,
                              backup_ssh_path,
                              backup_to_path,
                              test=False):
    if test:
        logger.warning('Test model enabled - collecting backup files disabled')
    else:
        logger.info('Collecting database backups')
    create_local_directory(backup_to_path)
    change_local_directory_permission(backup_to_path)
    backup_files = generate_backup_file_paths(timestamp,
                                              backup_dbname,
                                              backup_ssh_path)
    scp_client = scp.SCPClient(backup_ssh_client.get_transport())
    for file in backup_files:
        copy_file_to = backup_to_path + "/"
        logger.debug(f'file: {file} to: {copy_file_to}')
        if not test:
            logger.info(f'Collecting..')
            scp_client.get(file,
                           local_path=copy_file_to)
            logger.info(f'Collected')
            logger.info(f'Deleting from host..')
            ssh_stdin, ssh_stdout, ssh_stderr = backup_ssh_client.exec_command(f'rm {file}')
            exit_status = ssh_stdout.channel.recv_exit_status()
            if exit_status != 0:
                logger.error(f'Deleting database backup failed: {ssh_stderr.read()}')
                raise Exception(f'Deleting database backup failed: {ssh_stderr.read()}')
            else:
                logger.info(f'Deleted from host')
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
