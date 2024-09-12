import os
import pwd
import grp
import getpass

from source.log.logger import logger


def change_ssh_directory_permissions(ssh_client,
                                     user,
                                     directory):
    logger.debug(f"Checking permissions to path: '{directory}' for user: '{user}'")
    parts = directory.split('/')
    for i in range(len(parts), 1, -1):
        path = '/'.join(parts[:i])
        stdin, stdout, stderr = ssh_client.exec_command(f"getfacl --absolute-names {path} | grep {user}")
        output = stdout.read()
        if output and "r--" not in output.decode():
            logger.debug(f"Level {i} access for {user} on {path}: {output}")
        else:
            logger.debug(f"Level {i} with no access for {user} on {path}")
            ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(f'sudo setfacl -m u:{user}:rx {path}')
            exit_status = ssh_stdout.channel.recv_exit_status()
            if exit_status != 0:
                logger.error("Encountered error while granting read permission to user", ssh_stderr.read())
                raise Exception("Encountered error while granting read permission to user}", ssh_stderr.read())
            else:
                logger.debug(f"Read permissions to directory: {path} granted for user: {user}")
    ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(f'sudo setfacl -R -m u:{user}:rwx {directory}')
    exit_status = ssh_stdout.channel.recv_exit_status()
    if exit_status != 0:
        logger.error("Encountered error while granting read/write permission to user", ssh_stderr.read())
        raise Exception("Encountered error while granting read/write permission to user", ssh_stderr.read())
    else:
        logger.debug(f"Read/write permission to directory: {directory} granted for user: {user}")


def change_local_directory_permission(directory):
    user = getpass.getuser()
    uid = pwd.getpwnam(user).pw_uid
    gid = grp.getgrnam(user).gr_gid
    logger.debug(f"Checking permissions to path: '{directory}' for user: '{user}'")
    if os.access(directory, os.R_OK | os.W_OK | os.X_OK):
        logger.debug(f"Read/write/execute access already granted at path: '{directory}' for user: '{user}'")
    else:
        logger.debug(f"Modifying permissions at path: '{directory}' for user: '{user}'")
        os.chown(directory, uid, gid)
        os.chmod(directory, 0o700)
        logger.debug("Permission granted")
