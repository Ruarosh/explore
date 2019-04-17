/*
互斥锁
http://www.cnblogs.com/haippy/p/3237213.html
*/

#include <iostream>       // std::cout
#include <thread>         // std::thread
#include <mutex>          // std::mutex
#include <chrono>         // std::chrono::milliseconds

volatile int counter(0); // non-atomic counter
std::mutex mtx;           // locks access to counter
std::timed_mutex time_mtx;
void attempt_10k_increases() {
    for (int i=0; i<10000; ++i) {
        if (mtx.try_lock()) {   // only increase if currently not locked:
            ++counter;
            mtx.unlock();
        }
    }
}

void fireworks() {
  // waiting to get a lock: each thread prints "-" every 200ms:
  while (!time_mtx.try_lock_for(std::chrono::milliseconds(200))) {
    std::cout << "-";
  }
  // got a lock! - wait for 1s, then this thread prints "*"
  std::this_thread::sleep_for(std::chrono::milliseconds(1000));
  std::cout << "*\n";
  time_mtx.unlock();
}

int main (int argc, const char* argv[]) {
    std::thread threads[10];
#if 0
    for (int i=0; i<10; ++i)
        threads[i] = std::thread(attempt_10k_increases);

    for (auto& th : threads) th.join();
    std::cout << counter << " successful increases of the counter.\n";
#else
  // spawn 10 threads:
  for (int i=0; i<10; ++i)
    threads[i] = std::thread(fireworks);
  for (auto& th : threads) th.join();
#endif
    return 0;
}

