# Logging-Framework
  A logging framework that logs exceptions raised in an application to file and database and allows easier retrieval and deletion of logs. It can be used independently in multiple applications. It is implemented using flask in Python as a microservice.
  
## Usage:
  1. Clone this repository
  
    git clone https://github.com/REC-CHENNAI/Logging-Framework-Python_REC.git
  2. Install necessary packages
  
    pip install -r requirements.txt
  3. Run the microservice
  
    python Microservice/main.py
  4. Import Logger in your application
    <br>Ensure that Logger.py is in the same directory as the application
  
    from Logger import Logger
  5. Initialize and configure Logger<br>
    Log levels (from high to low) are : "ERROR", "WARNING", "INFO", "DEBUG"
  
    logger = Logger()
    logger.configure(app_id=123, db_storage=True, log_level="DEBUG")
  6. Calling methods such as info(), debug(), warning() based on log level writes log to file and database (if configured)
  
    logger.debug("<log_message>")
    logger.info("<log_message>")
    logger.warning("<log_message>")
  7. Call error() function with traceback as argument to log errors
  
    import traceback
    try:
        a = 1/0
    except Exception as e:
        logger.error("<log_message>", traceback.format_exc())
        
  8. Use log_batch() method to add log to a buffer. The logs in the buffer are written when it achieves the specified size
  
    logger.log_batch("<log_message>", "DEBUG")
  9. Use log_error_batch() to also add the error log to the buffer
    
    import traceback
    try:
        a = 1/0
    except Exception as e:
        logger.log_error_batch("<log_message>", traceback.format_exc())
  10. Finally, call close() method to process all the logs stored in the buffer.
  
    logger.close()
  11. Get log details by sending GET request to the endpoint along with necessary filters
  
    /getfile?app_id=123
    /getdb?log_level=ERROR
  12. Delete log details by sending GET request to the endpoint along with necessary filters
  
    /deletefile?app_id=123
    /deletedb?log_level=DEBUG

