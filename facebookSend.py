#!/usr/bin/python3
pageId='1493276620992822'
appId='1625014141088441'
appSecret='06bb3282b76ce64c5f483d4dc1303ca2'
pageAccessToken='EAAXF8RaicrkBAPpN6qRKWvaHpgO7KZAtxJArjqlVnnJyyMj7zABnsuYgSkdQLrbmtPpZBiQSCl0MIhKThhvLcUZAfbIPsAWrybKaAdefx4tFvL21AeyfpfE79ZAOAFKuf2KmOAUlxNSgIJktJ8VLcBRAHSRKJvVk7UNZAi5jRLAZDZD'


import facebook

def main():
  # Fill in the values noted in previous steps here
  cfg = {
    "page_id"      : pageId,  # Step 1
    "access_token" : pageAccessToken   # Step 3
    }

  api = get_api(cfg)
  msg = "Hello, world!"
  status = api.put_wall_post(msg)

def get_api(cfg):
  graph = facebook.GraphAPI(cfg['access_token'])
  # Get page token to post as the page. You can skip 
  # the following if you want to post as yourself. 
  #resp = graph.get_object('me/accounts')
  #page_access_token = None
  #for page in resp['data']:
  #  if page['id'] == cfg['page_id']:
  #    page_access_token = page['access_token']
  #graph = facebook.GraphAPI(page_access_token)
  return graph
  # You can also skip the above if you get a page token:
  # http://stackoverflow.com/questions/8231877/facebook-access-token-for-pages
  # and make that long-lived token as in Step 3

if __name__ == "__main__":
  main()
