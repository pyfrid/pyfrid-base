#  Copyright 2012 Denis Korolkov
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.



import threading
import Queue
import time

class FullThreadPoolError(Exception): pass

class ThreadPoolError(Exception): pass

class ThreadPool(object):
    
    def __init__(self, parent, num_threads=1, queue_size=0, persist=False, work_pause=0.1):
        self._parent=parent
        self._persist=persist
        self._work_pause=work_pause
        self._queue_size=queue_size
        self._queue=Queue.Queue(self._queue_size)
        self._workers=[]
        self._results=[]
        self._task_lock=threading.Lock()        
        for _ in range(num_threads):
            self._workers.append(Worker(self, self._work_pause))
        
    def add_task(self,func, *args, **kwargs):
        if not self._workers: raise ThreadPoolError("No workers in the pool")
        self._task_lock.acquire()
        try:
            self._results.append(None)
            resindex=len(self._results)-1
            self._queue.put((func, args, kwargs, resindex), block=False)
        except Queue.Full:
            raise FullThreadPoolError
        finally:
            self._task_lock.release()
    
    def _delete_workers(self):
        for worker in self._workers:
            worker.stop()
            worker.join()
            del worker
    
    def __del__(self):
        self._delete_workers()
                  
    def join_all(self):
        self._queue.join()
        if not self._persist:
            self._delete_workers()
        results=self._results[:]
        self._results=[]
        return results
       
        
        
class Worker(threading.Thread):
    
    def __init__(self, pool, pause):
        threading.Thread.__init__(self)
        self.pool = pool
        self.pause=pause
        self.stopped = False
        self.setDaemon(True)
        self.start()
    
    def stop(self):
        self.stopped=True
        
    def run(self):
        """ Until told to quit, retrieve the next task and execute
        it, calling the callback if any.  """
        while not self.stopped:
            try:
                cmd, args, kwargs, resindex = self.pool._queue.get(block=False)
            except:
                time.sleep(0.1)
            else:
                try:
                    result = cmd( *args, **kwargs )
                    if resindex!=None: self.pool._results[resindex]=result
                except Exception,err:
                    self.pool._parent.exception(err)
                finally: 
                    self.pool._queue.task_done()
                    time.sleep(self.pause)
