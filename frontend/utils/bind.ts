export const bindArgs = (bindedArgs: any[], fn: Function) => {
    return (...args: any[]) => {
        return fn.apply(null, bindedArgs.concat(args));
    };
};

export const bindArg = <Arg, RestArgs extends any[], Result>(
    arg: Arg,
    fn: (a: Arg, ...rest: RestArgs) => Result
): ((...rest: RestArgs) => Result) => {
    return bindArgs([arg], fn);
};
