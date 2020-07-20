# 爬虫demo

# Instruction
    1. demos are not maintained by now except tb_spider, they may works or need to debug. Because most of them are created long time ago.
    But they can be used to review.
    2. tb_spider:
        I try to implement taobao spider by using 2 method(requests and selenium).Here is the instruction of tb_spider files:
            > config.py: Spider configuration includes Database stuff
            > main.py: Crawl all the commodities base info in the index page after searching the key word.(Using selenium)
            > details_by_requests(selenium): Crawl the detail info about each commodity collected by main.py(requests or selenium)
            > multiprocess_test.py: Accelerate spider by using multi processes, which only achieve selenium way till this moment.
            > parse_url: parse the data string which added in request params when sending request.
