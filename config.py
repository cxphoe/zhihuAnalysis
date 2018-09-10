EFFECTIVE_TIMES = 1 # 一个代理有效的次数，每次连接失败就减 1，直到 0 被清除
TIMEOUT = 5

MAX_CRAWL_CONCURRENT_PER_PROCESS = 30 # 爬取时每个进程的最大并发
MAX_CRAWL_PROCESS = 2 # 最大的并发进程
TASK_QUEUE_SIZE = 50 # 任务队列SIZE
CHECK_WAIT_TIME = 1 # 进程数达到上限时的等待时间
CRAWL_WAIT_TIME = 1 # 每个协程爬取一个用户之后的等待时间