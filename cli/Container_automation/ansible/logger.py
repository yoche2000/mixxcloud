import logging

def get_logger(tenant_name):
    loggers = {}
    logger = logging.getLogger(tenant_name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Create a file handler specifically for this tenant
    # The mode 'a' (append) is default and is explicitly set here for clarity
    file_handler = logging.FileHandler(f'logs/{tenant_name}_api_log.log', mode='a')
    file_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    loggers[tenant_name] = logger
    return loggers[tenant_name]

def log_api_call(tenant_name, api_call):
    logger = get_logger(tenant_name)
    logger.info(f'API Call: {api_call}')

# Usage - # Import the log_api_call into the caller functions.
# log_api_call('TenantA', f'CreateBridge')

