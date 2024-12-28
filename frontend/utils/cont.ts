export const cont =
    <State, Result>(a: State) =>
    (fn: (a: State) => Result) =>
        fn(a);
