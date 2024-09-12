import os
import pwd
import grp

from source.log.logger import logger


def create_ssh_directory(ssh_client,
                         directory):
    ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(f'ls {directory}')
    exit_status = ssh_stdout.channel.recv_exit_status()
    if exit_status != 0:
        logger.warning("Directory does not exist: %s", ssh_stderr.read())
        ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(f'mkdir -p {directory}')
        exit_status = ssh_stdout.channel.recv_exit_status()
        if exit_status != 0:
            logger.error("Encountered error while creating directory:", ssh_stderr.read().decode('utf-8'))
            raise Exception("Encountered error while creating directory:", ssh_stderr.read().decode('utf-8'))
        else:
            logger.debug(f"Directory created: {directory}")
    else:
        logger.debug(f"Directory exist: {directory}")


def create_local_directory(directory):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory, mode=0o777)
            logger.debug(f"Directory created: {directory}")
        except PermissionError as e:
            logger.exception(f"Permission denied when trying to create directory: {directory}",
                             exc_info=True)
            raise
    else:
        logger.debug(f"Directory exists: {directory}")
