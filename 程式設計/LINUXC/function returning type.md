The wording of a "function returning _type_" just means a function defined as returning some type `T`, such as `T f() { .... }`.

The quoted clause just tells you that using the designator of the function, for example its name `f`, in an expression, would have the type "pointer to a function returning T". To be read with the following associative priorities: "pointer to " "a function returning T".

The wording avoids to say the name of the function, since the rule is anything that designates a function, including a dereferenced function pointer.

Example, with T being `void`:

```c
void f(){ printf("Oops\n");}

int main(void) {
    void (*pf1)(), (*pf2)(); 
    void (*a[3])();  

    pf2 = &f;   // &f is the address of f, so a pointer to a function returning void
    pf1 = f;    // f is a function designator,  it's converted to a function pointer
    a[0]=f;     // same, but for the fun it's stored in an array of function pointers
    printf ("%lx %lx %lx %lx %lx\n", f, &f,  pf1, pf2, a[0]);  // all the same
    pf2();      // will call the function as well.  pf2 is already a function pointer
    
    (*pf1)();     // here we see that *pf1 is also a function designator
    pf2 = *pf1;   // *pf1 is converted to a function pointer, so it's pf1   
    printf ("%lx %lx\n", pf1, pf2);    // all the same 

    (***************pf1)(); // Sorry: I couldn't resist ;-)

    return 0;
}
```