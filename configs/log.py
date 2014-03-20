__author__ = 'alivinco'

config = {
    'version': 1,
    'disable_existing_loggers': False,  # this fixes the problem
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'INFO',
            'class':'logging.StreamHandler',
        },
        'info_file_handler': {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": "info.log",
            "maxBytes": "10485760",
            "backupCount": "20",
            "encoding": "utf8"
        },

        'error_file_handler': {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "standard",
            "filename": "errors.log",
            "maxBytes": "10485760",
            "backupCount": "20",
            "encoding": "utf8"
        }
    },
    'loggers': {
        '': {
            'handlers': ['info_file_handler'],
            'level': 'INFO',
            'propagate': True
        }
    }
}