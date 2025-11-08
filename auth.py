"""
- Class to authenticate the client on 5Paisa and xts: at both ends
"""

## Necessary import statements
from py5paisa import FivePaisaClient
from pickleFile import PickleClass
from Connect import XTSConnect


## XTS Class
class XTSClient:
    __XTS_CRED_FILE = 'Cred\\credentials_xts.pkl'
    
    ## Constructor
    def __init__(self, needAuth:bool=True):
        self.xtsObj = None
        self.pickleObj = PickleClass(XTSClient.__XTS_CRED_FILE)
        if(needAuth == True):
            self.authenticate()
        else:
            self.getter()

    ## Method to authenticate xts
    def authenticate(self) -> bool:
        status = False
        credentials = self.pickleObj.read()
        if(credentials):
            self.xtsObj = XTSConnect(credentials['INTERACTIVE_API_KEY'], credentials['INTERACTIVE_API_SECRET_KEY'], credentials['SOURCE'])
            response = self.xtsObj.interactive_login()
            if (response['type'] == 'success' and 'token' in response['result']):
                xts_token = response['result']['token']
                xts_userid = response['result']['userID']
                xts_investor_client = response['result']['isInvestorClient']
                credentials['token'] = xts_token
                credentials['userID'] = xts_userid
                credentials['isInvestorClient'] = xts_investor_client
                status = self.pickleObj.write(credentials)
                if(status == True):
                    print('Successfully written XTS credentials - with today token')
                    print('Success :: XTS interactive client connected\n')
                else:
                    print('Failed to write the XTS credentials - with today token')
            else:
                print('Failed :: XTS interactive client not connected\n')
        else:
            print('Failed :: To load or read the XTS credentials')
        return status

    ## Method to get the authenticated object
    def getter(self) -> None:
        credentials = self.pickleObj.read()
        if(credentials):
            self.xtsObj = XTSConnect(credentials['INTERACTIVE_API_KEY'], credentials['INTERACTIVE_API_SECRET_KEY'], credentials['SOURCE'])
            self.xtsObj._set_common_variables(credentials['token'], credentials['userID'], credentials['isInvestorClient'])
            print('Success :: XTS interactive client connected\n')
        else:
            print('Failed :: To load or read the XTS credentials')


## 5Paisa Class
class Broker5Paisa:
    __5PAISA_LOGIN_URL = 'https://dev-openapi.5paisa.com/WebVendorLogin/VLogin/Index?VendorKey={0}&ResponseURL={1}'
    __5PAISA_CRED_FILE = 'Cred\\credentials_5paisa.pkl'

    ## Constructor
    def __init__(self, needAuth:bool=True):
        self.brokerObj = None
        self.pickleObj = PickleClass(Broker5Paisa.__5PAISA_CRED_FILE)
        if(needAuth == True):
            self.authenticate()
        else:
            self.getter()

    ## Method to authenticate 5Paisa
    def authenticate(self) -> bool:
        status = False
        credentials = self.pickleObj.read()
        if(credentials):
            self.brokerObj = FivePaisaClient(cred=credentials)
            print(f'Login using the URL: {Broker5Paisa.__5PAISA_LOGIN_URL.format(credentials["USER_KEY"], "https://www.google.com/")}')
            response_token = input('Enter the received response token:')
            self.brokerObj.get_oauth_session(response_token)
            access_token = self.brokerObj.get_access_token()
            self.brokerObj.set_access_token(access_token, credentials['CLIENT_CODE'])
            credentials['ACCESS_TOKEN'] = access_token
            credentials['RESPONSE_TOKEN'] = response_token
            status = self.pickleObj.write(credentials)
            if(status == True):
                print('Successfully written 5Paisa credentials - with today token')
                print('Success :: 5Paisa client connected\n')
            else:
                print('Failed to write the 5Paisa credentials - with today token')
        else:
            print('Failed :: To load or read the 5paisa credentials')
        return status

    ## Method to get the authenticated token
    def getter(self) -> None:
        credentials = self.pickleObj.read()
        if(credentials):
            self.brokerObj = FivePaisaClient(cred=credentials)
            self.brokerObj.set_access_token(credentials['ACCESS_TOKEN'], credentials['CLIENT_CODE'])
            print('Success :: 5Paisa client connected\n')
        else:
            print('Failed :: To load or read the 5paisa credentials')
