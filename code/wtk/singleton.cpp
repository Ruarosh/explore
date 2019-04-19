/*
https://segmentfault.com/a/1190000015950693
https://www.cnblogs.com/liyuan989/p/4264889.html
*/

// DCL, double-checked locking
template<typename T>
class Singleton
{
public:
    static T& getInstance()
    {
        if(!value_)
        {
            MutexGuard guard(mutex_);
            if (!value_)
            {
                value_ = new T();
            }
        }
        return *value_;
    }
 
private:
    Singleton();
    ~Singleton();
 
    static T*     value_;
    static Mutex  mutex_;
};
 
template<typename T>
T* Singleton<T>::value_ = NULL;
 
template<typename T>
Mutex Singleton<T>::mutex_;
