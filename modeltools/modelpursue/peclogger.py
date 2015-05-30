__author__ = 'imalkov'

import logging
import os
import pprint
import timeit
import time

class ModelLogger:
    def __init__(self, driver):
        self._driver = driver
        log_name = '{0}/log_{1}.txt'.format(os.environ['HOME'], os.getpid())
        print('ModelLogger - log file: {0}'.format(log_name))
        logging.basicConfig(filename=log_name,level=logging.DEBUG)
        self._logger = logging.getLogger('Model Logger')


class EnvLogger(ModelLogger):
    def __init__(self, driver):
        super.__init__(driver)

    def __call__(self, *args, **kwargs):
        pass

class ExecLogger(ModelLogger):
    model_state_dict = {
        0: 'init_state',
        1: 'pec_props_state',
        2: 'by_tasks_state',
        3: 'pool_exe_state',
        4: 'exec_complete_state',
        5: 'app_complete_state'}

    def __init__(self, driver):
        super().__init__(driver)

    def init_state(self):
        self._logger.info('Model Executor state: INIT ')
        s = ''
        s += '\n\tmax pool size = {0}'.format(self._driver.max_pool_size)
        s += '\n\tmodel = {0}'.format(self._driver.pec_model)
        self._logger.info(s)

    def pec_props_state(self):
        self._logger.info('Model Executor state: PEC_PROPS')
        s = ''
        s += 'working list:\n\t'
        s += '\n\t'.join(self._driver.wrk_list)
        self._logger.info(s)

    def by_tasks_state(self):
        self._logger.info('Model Executor state: BY_TASKS')
        s = ''
        s = '\n{0}'.format(pprint.pformat(self._driver.bytask_list))
        self._logger.info(s)

    def pool_exe_state(self):
        self._logger.info('Model Executor state: POOL_EXE')
        s = ''
        s += 'EXECUTING POOL:\n\t{0}'.format('\n\t'.join(self._driver._sub_array))
        s += '\n\tDATE_TIME: {0}'.format(time.strftime("%x"))
        self.exec_start_time = timeit.default_timer()
        self._logger.info(s)

    def exec_complete_state(self):
        self._logger.info('Model Executor state: EXEC_COMPLETE')
        s = ''
        s += '\nfinished in {0} sec'.format(int(timeit.default_timer() - self.exec_start_time))
        self._logger.info(s)

    def app_complete_state(self):
        self._logger.info('Model Executor state: APP_COMPLETE')
        if self._driver.dry_run is True:
            s = 'DRY RUN'
        else:
            s = 'MODEL RUN'
        self._logger.info('^^^^^^^^^^^^ {0} EXECUTION COMPLETED ^^^^^^^^^^^^^^^^^ '.format(s))

    def __call__(self):
        getattr(self, ExecLogger.model_state_dict[self._driver._state])()

class AnalysisLogger:
    def __init__(self, driver):
        super.__init__(driver)

    def __call__(self, *args, **kwargs):
        pass