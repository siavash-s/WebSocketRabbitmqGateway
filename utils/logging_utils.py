from logging.config import dictConfig


def set_syslog_logging(syslog_addr="/dev/log", level='INFO', prefix=''):
    if level not in ("INFO", "DEBUG", "WARNING"):
        raise ValueError("LOG_LEVEL should be one of INFO, DEBUG or WARNING")
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '{} [%(asctime)s] %(levelname)s in %(module)s: %(message)s'.format(prefix)
        }},
        'handlers': {'syslog': {
            'class': 'logging.handlers.SysLogHandler',
            'address': syslog_addr,
            'formatter': 'default',
        }},
        'root': {
            'level': level,
            'handlers': ['syslog']
        }
    })
