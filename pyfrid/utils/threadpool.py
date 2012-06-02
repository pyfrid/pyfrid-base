#    This file is part of PyFRID.
#
#    PyFRID is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyFRID is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyFRID.  If not, see <http://www.gnu.org/licenses/>.
#



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
