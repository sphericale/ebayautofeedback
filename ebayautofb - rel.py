import os
import stat
import random
from ebaysdk.trading import Connection as Trading

debug = False

# The following 4 variables MUST be set appropriately for this script to work
# Get your eBay SDK keys at https://developer.ebay.com/

user_token = "xxxxxxxxxxxx"
_appid = "xxxxxxxxxxxxx"
_devid = "xxxxxxxxxxxx"
_certid = "xxxxxxxxxxx"

script_fn = os.path.realpath(__file__)
si = os.stat(script_fn)
if bool(si.st_mode & stat.S_IROTH):
    print("Warning: script file is world readable - your eBay SDK keys may be viewed by other users!")

feedback_text=(
                "Great buyer, thanks!",
                "Recommended eBayer, thank you",
                "Good transaction, thank you"
              )
              
try:    
    print("Fetching items awaiting feedback...")
    api = Trading(appid=_appid, devid=_devid, certid=_certid, token=user_token, config_file=None)
    response = api.execute('GetItemsAwaitingFeedback', {})
    if debug:
        print(response.dict())
    print("Server response: {}".format(response.dict()['Ack']))
    i = 0
    for c,transaction in enumerate(response.dict()['ItemsAwaitingFeedback']['TransactionArray']['Transaction']):
        buyer_id=transaction['Buyer']['UserID']
        item_title=transaction['Item']['Title']
        transaction_id=transaction['TransactionID']
        orderlineitem_id=transaction['OrderLineItemID']
        try:
            fb_received=transaction['FeedbackReceived']['CommentType']
        except Exception as e:
            fb_received=""
        if fb_received == "Positive":
            response = api.execute('LeaveFeedback', {'OrderLineItemID': orderlineitem_id,'CommentType': 'Positive','CommentText':random.choice(feedback_text)})
            print("Left feedback for user: {}, order_id: {}, item: {}".format(buyer_id,orderlineitem_id,item_title))
            i+=1
    print("Feedback left for {} transactions out of {}".format(i,c))
except ConnectionError as e:
    print(e)
    print(e.response.dict())
