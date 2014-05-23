__author__ = 'alivinco'

config = {
    'version': 1,
    'disable_existing_loggers': True,  # this fixes the problem
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': "standard"
        },
        'info_file_handler': {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
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
        'werkzeug': {
            'handlers': ['default'],
            'level': 'ERROR',
            'propagate': False
        },
        'bf_web':{
            "handlers": ["default", "info_file_handler", "error_file_handler"],
            'level':'INFO',
            'propagate': True
        },
        'bf_msg_pipeline':{
            "handlers": ["default", "info_file_handler", "error_file_handler"],
            'level':'DEBUG',
            'propagate': True
        },
        'bf_mqtt':{
            "handlers": ["default", "info_file_handler", "error_file_handler"],
            'level':'INFO',
            'propagate': True
        },
        'bf_cache':{
            "handlers": ["default", "info_file_handler", "error_file_handler"],
            'level':'INFO',
            'propagate': True
        },
        'bf_msg_manager':{
            "handlers": ["default", "info_file_handler", "error_file_handler"],
            'level':'DEBUG',
            'propagate': True
        }
    }
}