#include <iostream>
#include <string>
#include <vector>

using namespace std;

/***wtk-function***************digit => all chars cominitions************************ */
void dfs_search(string num, string dict[], int level, string out, vector<string>& res) {
    if(level == num.length()) {
        res.push_back(out);
        return;
    }

    int len = dict[num[level] - '2'].length();
    for(auto i = 0; i < len; ++i) {
        out.push_back(dict[num[level] - '2'][i]);
        dfs_search(num, dict, level+1, out, res);
        out.pop_back();
    }
}

int main_digit_chars() {
    string dict[] = {"abc", "def", "ghi", "jkl", "mno"};
    vector<string> res;
    string num = "23";

    dfs_search(num, dict, 0, "", res);
    
    for(auto& str : res) {
        cout << str << endl;
    }

    return 0;
}
/***********************digit => all chars cominitions**************************/

/***wtk-function**************** brackets problems **********************************/
void dfs_brackets(int left, int right, string out, vector<string>& res) {
    if(left > right) {
        return;
    }
    if(left == right && left == 0) {
        res.push_back(out);
        return;
    }

    if(left > 0) {
        dfs_brackets(left-1, right, out+"(", res);
    }
    
    if(right > 0) {
        dfs_brackets(left, right-1, out+")", res);
    }
}

int main_brackets_generated() {
    int n = 4;
    vector<string> res;    
    dfs_brackets(n, n, "", res);
    for(auto& str : res) {
        cout << str << endl;
    }
    return 0;
}
/************************** brackets problems **********************************/

/*****wtk-function**************** reverse link **********************************/
typedef struct ListNode {
    int val;
    struct ListNode* next;
}ListNode;

ListNode* swap_pairs(ListNode* head) {
    if(!head || !head->next) {
        return head;
    }

    ListNode* t = head->next;
    head->next = swap_pairs(head->next->next);
    t->next = head;

    return t;
}

ListNode* init_link() {
    ListNode* n1 = new ListNode{1,NULL};
    ListNode* n2 = new ListNode{2,n1};
    ListNode* n3 = new ListNode{3,n2};
    ListNode* n4 = new ListNode{4,n3};

    return n4;
}

int main_reverse_link() {
    ListNode* head = init_link();
    ListNode* res = swap_pairs(head);
    while(res) {
        cout << res->val << endl;
        res = res->next;
    }

    return 0;
}
/************************** reverse link **********************************/

/****wtk-function***************small head heap ********************************/
#include <stdio.h>
#include <stdlib.h>

#define K (10)
int arr[K+1];
int all_data[1000];

void swap_val(int n1, int n2) {
    int t = arr[n1];
    arr[n1] = arr[n2];
    arr[n2] = t;
}

void shift_down(int n) {
    int t, tmp = n*2;

    while(n*2 <= K) {
        if(arr[n] > arr[n*2]) {
            t = 2*n;
        } else {
            t = n;
        }

        if(n*2+1 <= K) {
            if(arr[t] > arr[n*2+1]) {
                t = n*2 + 1;
            }
        }

        if(t == n) {
            break;
        }

        swap_val(n, t);
        n = t;
    }
}

// int deletemax() {
//     int t;
//     t=arr[1];
//     arr[1]=arr[n];
//     n--;
//     shift_down(1);
//     return t;
// }

void create_min_heap() {
    for(int i = K/2; i >= 1; --i) {
        shift_down(i);
    }
}

void init() {
    int i;
    for(i = 1; i <= 10; ++i) {
        arr[i] = i;
    }
    for(i = 1; i <= 1000; ++i) {
        all_data[i-1] = i;
    }
}

void output_arr(int* arr, int size) {
	for(int i = 0; i < size; i++) {
        std::cout << arr[i] << std::endl;
    }
}

void heap_sort_main() {
    init();
    create_min_heap();
//  output_arr(arr+1, 10);
    //将剩下的数与堆顶做比较
    for(int i=k;i<len;i++) {
        if(nums[i]>res[0]) {  //当前数比堆顶数大
            res[0]=nums[i]; //将堆顶更新为该数
            adjustMinHeap(res,0,k); //重新调整堆
        }
    }
 }


/**************************small head heap ********************************/

int main() {
    heap_sort_main();
    return 0;
}
