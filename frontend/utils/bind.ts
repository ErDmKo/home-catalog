export const bindArgs = (bindedArgs: any[], fn: Function) => {
    return (...args: any[]) => {
        return fn.apply(null, bindedArgs.concat(args));
    };
};

function bindArgFn<Arg, Arg1, Result>(arg: Arg, fn: (a: Arg, b: Arg1) => Result): (b: Arg1) => Result;
function bindArgFn<Arg, RestArgs extends any[], Result>(arg: Arg, fn: (a: Arg, ...rest: RestArgs) => Result) {
  return bindArgs([arg], fn);
};

export const bindArg = bindArgFn;
