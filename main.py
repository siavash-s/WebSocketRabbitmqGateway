import os
from utils.logging_utils import set_syslog_logging


if __name__ == "__main__":

    # set default logging to syslog, according to ENV variable provided
    syslog_addr = os.environ.get("SYSLOG_ADDRESS", default='/dev/log')
    level = os.environ.get("LOG_LEVEL", default='INFO').upper()
    prefix = os.environ.get("LOG_PREFIX", default="WebsocketGateway")
    set_syslog_logging(syslog_addr=syslog_addr, level=level, prefix=prefix)
