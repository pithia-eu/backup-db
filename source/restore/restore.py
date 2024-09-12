import scp
from source.log.logger import logger
from source.utils.environment import get_env_variable
from source.utils.ssh import create_ssh_client
from source.utils.directory import (create_ssh_directory)
from source.utils.permissions import change_permissions

BACKUP_FILE_PATTERN_DB = "{backup_to_path}/{backup_dbname}_db_{timestamp}.{ext}"


def generate_backup_file_path(timestamp,
                              backup_dbname,
                              backup_to_path):
    return BACKUP_FILE_PATTERN_DB.format(backup_to_path=backup_to_path,
                                         backup_dbname=backup_dbname,
                                         timestamp=timestamp,
                                         ext="sql")


def generate_restore_command(timestamp,
                             restore_postgres_user,
                             backup_dbname,
                             restore_ssh_path):
    backup_file = generate_backup_file_path(timestamp,
                                            backup_dbname,
                                            restore_ssh_path)
    return f'sudo su {restore_postgres_user} -c "psql -U postgres -d {backup_dbname}_bk < {backup_file}"'


def upload_database_backups(restore_ssh_client,
                            timestamp,
                            restore_postgres_user,
                            restore_ssh_path,
                            backup_dbname,
                            backup_to_path,
                            test=False):
    if test:
        logger.warning('Test model enabled - uploading backup files disabled')
    else:
        logger.info('Uploading database backups to backup host')
    create_ssh_directory(restore_ssh_client,
                         restore_ssh_path)
    change_permissions(restore_ssh_client,
                       restore_postgres_user,
                       restore_ssh_path)
    backup_file = generate_backup_file_path(timestamp,
                                            backup_dbname,
                                            backup_to_path)
    scp_client = scp.SCPClient(restore_ssh_client.get_transport())
    copy_file_to = restore_ssh_path + "/"
    logger.debug(f'file: {backup_file} to: {copy_file_to}')
    if not test:
        logger.info(f'Uploading..')
        scp_client.put(backup_file,
                       copy_file_to)
        logger.info(f'Uploaded')
    scp_client.close()


def restore_database_backup(restore_ssh_client,
                            timestamp,
                            restore_postgres_user,
                            backup_dbname,
                            restore_ssh_path,
                            test):
    if test:
        logger.warning('Test model enabled - restore disabled')
    else:
        logger.info('Restoring database backup')
    command = generate_restore_command(timestamp,
                                       restore_postgres_user,
                                       backup_dbname,
                                       restore_ssh_path)
    logger.debug(f'Command: {command}')
    if not test:
        logger.info(f'Restoring database backup with command: {command}')
        ssh_stdin, ssh_stdout, ssh_stderr = restore_ssh_client.exec_command(
            f"sudo su {restore_postgres_user} -c 'psql -U {restore_postgres_user} -l'")
        exit_status = ssh_stdout.channel.recv_exit_status()
        if exit_status != 0:
            logger.error(f'Listing server DBs failed: {ssh_stderr.read()}')
            raise Exception(f'Listing server DBs failed: {ssh_stderr.read()}')
        else:
            dbs = ssh_stdout.read().decode("utf-8")
            logger.debug(f'Backup server DBs:\n {dbs}')
            if f'{backup_dbname}_bk' in dbs:
                logger.debug(f'Restore DB exists: {backup_dbname}_bk')
            else:
                logger.debug(f'Restore DB does not exist: {backup_dbname}_bk. Creating..')
                ssh_stdin, ssh_stdout, ssh_stderr = restore_ssh_client.exec_command(
                    f"sudo su {restore_postgres_user} -c 'createdb {backup_dbname}_bk'")
                exit_status = ssh_stdout.channel.recv_exit_status()
                if exit_status != 0:
                    logger.error(f'Creation of backup DBs failed: {ssh_stderr.read()}')
                    raise Exception(f'Creation of backup DBs failed: {ssh_stderr.read()}')
                else:
                    logger.debug(f'Backup DBs created: {backup_dbname}_bk')
        ssh_stdin, ssh_stdout, ssh_stderr = restore_ssh_client.exec_command(command)
        exit_status = ssh_stdout.channel.recv_exit_status()
        if exit_status != 0:
            logger.error(f'Restoring database backup failed: {ssh_stderr.read()}')
            raise Exception(f'Restoring database backup failed: {ssh_stderr.read()}')
        else:
            logger.info(f'Restoring database backup completed:\n {ssh_stdout.read()}')
        ssh_stdin, ssh_stdout, ssh_stderr = restore_ssh_client.exec_command(
            f'sudo -u {restore_postgres_user} psql -d {backup_dbname}_bk -c '
            f'"SELECT table_name FROM information_schema.tables WHERE table_schema=\'public\'"')
        exit_status = ssh_stdout.channel.recv_exit_status()
        if exit_status != 0:
            logger.error(f'Reading tables from restored DB failed: {ssh_stderr.read()}')
            raise Exception(f'Reading tables from restored DB failed: {ssh_stderr.read()}')
        else:
            logger.info(f'Reading tables from restored DB completed:\n {ssh_stdout.read().decode()}')
        logger.info(f'Deleting backup file from host..')
        backup_file = generate_backup_file_path(timestamp,
                                                backup_dbname,
                                                restore_ssh_path)
        ssh_stdin, ssh_stdout, ssh_stderr = restore_ssh_client.exec_command(f'rm {backup_file}')
        exit_status = ssh_stdout.channel.recv_exit_status()
        if exit_status != 0:
            logger.error(f'Deleting database backup file failed: {ssh_stderr.read()}')
            raise Exception(f'Deleting database backup file failed: {ssh_stderr.read()}')
        else:
            logger.info(f'Backup file Deleted from host')


def restore(timestamp,
            test=False):
    logger.info('Restoring Postgres Server..')
    restore_ssh_key_path = get_env_variable("RESTORE_SSH_KEY_PATH")
    restore_ssh_host = get_env_variable("RESTORE_SSH_HOST")
    restore_ssh_port = int(get_env_variable("RESTORE_SSH_PORT"))
    restore_ssh_user = get_env_variable("RESTORE_SSH_USER")
    restore_postgres_user = get_env_variable("RESTORE_POSTGRES_USER")
    restore_ssh_path = get_env_variable("RESTORE_SSH_PATH")
    backup_dbname = get_env_variable("BACKUP_DBNAME")
    backup_to_path = get_env_variable("BACKUP_TO_PATH")
    restore_ssh_client = create_ssh_client(restore_ssh_host,
                                           restore_ssh_port,
                                           restore_ssh_user,
                                           restore_ssh_key_path)
    upload_database_backups(restore_ssh_client,
                            timestamp,
                            restore_postgres_user,
                            restore_ssh_path,
                            backup_dbname,
                            backup_to_path,
                            test)
    restore_database_backup(restore_ssh_client,
                            timestamp,
                            restore_postgres_user,
                            backup_dbname,
                            restore_ssh_path,
                            test)
    restore_ssh_client.close()
    logger.info('Restoring Postgres Server completed')
