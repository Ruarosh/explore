#include <iostream>
#include "../Include/ConcreteObserver.h"
#include "../Include/ConcreteSubject.h"

using namespace std;

int main(void)
{
    // 初始化观察者对象
    ConcreteObserver *A = new ConcreteObserver("小张");
    ConcreteObserver *B = new ConcreteObserver("小亮");
    ConcreteObserver *C = new ConcreteObserver("小红");

    // 初始化主题类
    ConcreteSubject *subject = new ConcreteSubject();

    // 向主题类中添加观察者对象
    subject->RegisterObserver(A);
    subject->RegisterObserver(B);
    subject->RegisterObserver(C);

    // 主题类执行群发操作(可以理解为前台小姐姐通知员工老板来没来)
    subject->NotifyObserver("老板来了");
    subject->NotifyObserver("吓吓你们");

    system("Pause");

    return 0;
}
