import sys
from networks.logging import logger


class NetworkSecurityException(Exception):          # inherits from Python's base Exception class
    def __init__(self, error_message, error_details: sys):
        self.error_message = error_message            # save the original error (this is 'e')

        _, _, exc_tb = error_details.exc_info()        # same call we just did — we ignore type & value (the _ _),
                                                        # we only want exc_tb here

        self.lineno = exc_tb.tb_lineno                  # store the line number
        self.file_name = exc_tb.tb_frame.f_code.co_filename  # store the file name

    def __str__(self):
        # __str__ controls what gets printed when you do print(this_exception)
        return (
            f"Error occurred in python script name [{self.file_name}] "
            f"line number [{self.lineno}] error message [{self.error_message}]"
        )
if __name__=='__main__':
    try:
        logger.logging.info("enter try block")
        a=1/0
        print("this will not be printed")
    except Exception as e:
        NetworkSecurityException(e,sys)



