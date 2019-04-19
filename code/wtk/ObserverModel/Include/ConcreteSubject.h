#ifndef __CONCRETESUBJECT_H__
#define __CONCRETESUBJECT_H__

#include "../Include/Subject.h"
#include "../Include/Observer.h"
#include <list>
#include <string>
#include <memory>

/*
 * 具体的主题实现类
 * 将有关状态存入具体的观察者对象
 * 在具体主题的内部状态改变时给所有登记过的观察者发出通知
 */
class ConcreteSubject : public CSubject 
{
public:
    ConcreteSubject() {
        pObservers_ = new std::list<std::shared_ptr<CObserver>>();
    }

    void RegisterObserver(CObserver *observer) {
        pObservers_->push_back(std::shared_ptr<CObserver>(observer));
    }

    void RemoveObserver(CObserver *observer) {
        if (pObservers_->size() > 0) {
            pObservers_->remove(std::shared_ptr<CObserver>(observer));
        }
    }

    void NotifyObserver(const std::string& msg) {
        std::cout << "群消息: " << msg << std::endl;
        auto iter = pObservers_->begin();
        for (; iter != pObservers_->end(); ++iter) {
            (*iter)->Update(msg);
        }
    }

private:
    std::list<std::shared_ptr<CObserver>> *pObservers_;
};

#endif
