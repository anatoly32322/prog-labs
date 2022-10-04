import asyncio
import os
import stat
import hashlib
from multiprocessing import Process, Value
from time import sleep
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
data_path = 'template.tbl'
with open(data_path) as f:
    password = f.readline()
is_working = Value('b', True)


class Manager:
    def __init__(self):
        pass

    @staticmethod
    def check_password():
        password_ = hashlib.sha256(input('Enter the password:\n').encode()).hexdigest()
        logger.info(
            '''
            expected password {}
            received password {}
            '''.format(password, password_)
        )
        return password_.strip() == password.strip()

    @staticmethod
    def check_file(path):
        return os.access(path, os.F_OK) \
               and not os.access(path, os.R_OK) \
               and not os.access(path, os.W_OK) \
               and not os.access(path, os.X_OK)

    async def run_permission_manager(self):
        global is_working
        while True:
            try:
                files = os.listdir()
                print(is_working.value)
                with open(data_path) as f:
                    f.readline()
                    for filename in f:
                        for real_filename in files:
                            if not is_working.value and filename.strip() == real_filename.strip().split('.')[0]\
                                    and self.check_file(real_filename):
                                os.chmod(real_filename, 0o754)
                                logger.info('permissions for file {} was recovering'.format(real_filename))
                            if is_working.value and filename.strip() == real_filename.strip().split('.')[0]\
                                    and not self.check_file(real_filename):
                                os.chmod(real_filename, 0o000)
                                logger.info('permissions for file {} was denied'.format(real_filename))

                sleep(10)
            except KeyboardInterrupt:
                continue

    def process_manager(self):
        asyncio.run(self.run_permission_manager())


async def main():
    global is_working

    main_process = Process(target=Manager().process_manager)
    main_process.start()

    while True:
        mode = input()
        if mode == 'help':
            print(
                '''
                help - print list of command
                switch off - returns file reading modes
                switch on - enables protection mode
                add new file - adding new file in list
                exit - turns off the program
                '''
            )
        elif mode == 'switch off':
            is_working.value = False
            logger.info('program switched off')
        elif mode == 'switch on':
            is_working.value = True
            logger.info('program switched on')
        elif mode == 'add new file':
            filename = input('Enter filename:\n')
            async with open(data_path, 'w') as f:
                await f.write('\n' + filename)
                logger.info('added new file {} into list'.format(filename))
        elif mode == 'exit':
            if Manager.check_password():
                exit()


if __name__ == '__main__':
    asyncio.run(main())
