import paramiko

from source.log.logger import logger


def create_ssh_client(ssh_host, ssh_port, ssh_user, ssh_key_path):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    client.connect(ssh_host, port=ssh_port, username=ssh_user, key_filename=ssh_key_path)
    logger.info('SSH Client created')
    return client
