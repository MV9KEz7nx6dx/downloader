import time
import nft_storage
from nft_storage.api import nft_storage_api
from nft_storage.model.error_response import ErrorResponse
from nft_storage.model.upload_response import UploadResponse
from nft_storage.model.unauthorized_error_response import UnauthorizedErrorResponse
from nft_storage.model.forbidden_error_response import ForbiddenErrorResponse
from pprint import pprint
import argparse

parser = argparse.ArgumentParser(description='Upload file to nft.storage')
parser.add_argument("--token", help="Connection token", default="")
parser.add_argument("--path", help="filepath", default="")
args = parser.parse_args()


# Defining the host is optional and defaults to https://api.nft.storage
# See configuration.py for a list of all supported configuration parameters.
configuration = nft_storage.Configuration(
    host = "https://api.nft.storage"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): bearerAuth
configuration = nft_storage.Configuration(
    access_token = args.token
)

# Enter a context with an instance of the API client
with nft_storage.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = nft_storage_api.NFTStorageAPI(api_client)
    body = open(args.path, 'rb') # file_type | 

    # example passing only required values which don't have defaults set
    try:
        # Store a file
        api_response = api_instance.store(body)
        pprint(api_response)
    except nft_storage.ApiException as e:
        print("Exception when calling NFTStorageAPI->store: %s\n" % e)
