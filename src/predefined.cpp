#include <iostream>
#include <stdio.h>
#include <string>
#include <cstdlib>

using namespace std;


void printInt(int n){
    cout << n << endl;
}

void printString(const string& s){
    cout << s << endl;
}

int readInt() {
    int n;
    cin >> n;
    return n;
}

string readString() {
    string s;
    cin.ignore();
    getline(cin, s);
    return s;
}

void error() {
    cerr << "runtime error" << endl;
    exit(1);
}

string Concat(const string& s1, const string& s2){
    return s1 + s2;
}