#ifndef MCTEST
#define MCTEST

#ifdef MC1

#define data1 0x20
 #define   data2 2.5f
#define data3 L"this is a data"
#define data4 true


#ifdef MC2

#define data5 'a'
#define data6 { {2.0, "abc"}, {1.5, "def"}, {5.6f, "7.2"}} 

#else

#define data5 {5.0, 7.5, 3.8}
#define data6 'c'

#endif 


#else

#define data1 1.0f   

#define data2 2
#define data3  false
#define data4 "this is a data"


#ifdef MC2

#define data5 'B'
#define data6 {1, 6, 3}
#define data7 0xa

#else

#define data5 'D'
#define data6 {1, 6}

#endif 

#endif 

#ifdef MC2
#undef MC2
#endif

#endif 