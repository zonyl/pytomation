from Queue import Queue
from threading import Thread

num_worker_threads = 5
source = [12, 34, 55, 234,234,344,4323,43,234,234,2,234,234,23,23,23,423,5,55,2,22,3,34,4,4,2,3,42,34,]

def worker(id):
    while True:
	item = ""
	for i in range(3):
		print "id" + str(id) + " i->" + str(i)
		pass
	try:
	        item = q.get(True)
	except:
		pass
#        do_work(item)
	print "ThreadID #" + str(id) + " Item->" + str(item)
        q.task_done()

q = Queue()
for i in range(num_worker_threads):
     t = Thread(target=worker, args=(i, ))
     print "Thread started" + str(i)
     t.daemon = True
     t.start()

for item in source:
    q.put(item)

q.join()       # block until all tasks are done

