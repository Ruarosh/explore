#ifndef __CONCRETEOBSERVER_H__
#define __CONCRETEOBSERVER_H__

#include "../Include/Observer.h"
#include <string>

/*
 * 具体观察者
 * 实现抽象观察者角色所要求的更新接口
 * 以便使本身的状态与主题的状态相协调
 */
class ConcreteObserver : public CObserver
{
public:
    ConcreteObserver(std::string name) {
        name_ = name;
    }

    void Update(const std::string& msg) {
        if ("老板来了" == msg) {
            // 做响应的操作
            std::cout << "老板是爹!我" << name_ << "乖乖工作!保证不再看不良视频!" << std::endl;
        }
        else {
            // 安心的继续上不良网站
            std::cout << "老子" << name_ << "怕谁了?老板不存在的!" << std::endl;
        }
    }

    std::string getName() {
        return name_;
    }

private:
    std::string name_;
};

#endif
