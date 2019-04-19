#include <iostream> 
#include <stdlib.h>
using namespace std; 

class Father
{
public:
    void Face()
    {
        cout << "Father's face" << endl;
    }

    void Say()
    {
        cout << "Father say hello" << endl;
    }
};


class Son:public Father
{
public:     
    void Say()
    {
        cout << "Son say hello" << endl;
    }
};

int main()
{
    Son son;
    Father *pFather=&son; // 隐式类型转换
    pFather->Say();

    return 0;
}
