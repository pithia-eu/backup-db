from datetime import datetime
from dotenv import load_dotenv

from source.log.logger import setup_logger
from source.utils.arguments import process_args
from source.utils.environment import get_env_variable
from source.backup.backup import backup
from source.restore.restore import restore

logger = setup_logger()


def main():

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    args = process_args()

    test = False

    if args.test:
        test = True
        logger.warning("Test mode in enabled. No backups will be created")
    else:
        logger.info('Database backup starts')

    load_dotenv()

    backup(timestamp, test)

    if get_env_variable("RESTORE"):
        restore(test)

    if args.test:
        logger.warning("Test run completed. No backups created")
    else:
       logger.info('Backup completed successfully')


if __name__ == '__main__':
    main()
