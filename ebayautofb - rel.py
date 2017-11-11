#!/usr/bin/env python3

import os
import stat
import random
from ebaysdk.trading import Connection as Trading

debug = False
# in test mode, no actual feedback will be left
test_mode = False

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

def get_ebay_items(api,page_no=1):
    if debug:
        print("get_ebay_items: page {}".format(page_no))
    return api.execute('GetItemsAwaitingFeedback', {'Pagination': {'PageNumber': page_no,'EntriesPerPage': 200}})

def leave_feedback(api,response):
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
        if debug:
            print("Transaction: Item {}, Buyer: {}, FB: {}, ID: {}".format(item_title,buyer_id,fb_received if fb_received != "" else "n/a",orderlineitem_id))
        if fb_received == "Positive":
            if test_mode:
                print("Test mode: Feedback would be left for user {}, item {}".format(buyer_id,item_title))
            else:
                response = api.execute('LeaveFeedback', {'OrderLineItemID': orderlineitem_id,'CommentType': 'Positive','CommentText':random.choice(feedback_text)})
                print("Left feedback for user: {}, order_id: {}, item: {}".format(buyer_id,orderlineitem_id,item_title))
            i+=1
    return i,c+1
                  
try:
    print("Fetching items awaiting feedback...")
    api = Trading(appid=_appid, devid=_devid, certid=_certid, token=user_token, config_file=None)
    response = get_ebay_items(api)
    if debug:
        print(response.dict())
    print("Server response: {}".format(response.dict()['Ack']))

    result_pages=int(response.dict()['ItemsAwaitingFeedback']['PaginationResult']['TotalNumberOfPages'])
    result_entries=int(response.dict()['ItemsAwaitingFeedback']['PaginationResult']['TotalNumberOfEntries'])
    print("Entries: {}, Pages: {}".format(result_entries,result_pages))

    def do_fb(a,r,page):
        i,c = leave_feedback(a,r)
        print("Page {}: Feedback left for {} transactions out of {}".format(page,i,c))
    
    # loop through each page, leaving feedback as we go
    # todo: would be better to build complete list of items first, then leave fb
    do_fb(api,response,1)
    for page in range(2,result_pages+1):
        response=get_ebay_items(api,page)
        do_fb(api,response,page)
        
except ConnectionError as e:
    print(e)
    print(e.response.dict())
