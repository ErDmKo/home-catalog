/**
 * Creates a memoized function.
 *
 * @param fn A function to memoize
 * @param rawKeyFn A function that determines the cache key
 * for storing the result based on the arguments provided to the function.
 * Defaults to the first argument.
 * The function is invoked only if no previous result is found for the key.
 */
export const memo = <Params extends any[], Result extends any, KeyType>(
  fn: (...args: Params) => Result,
  rawKeyFn?: (...keyArg: Params) => KeyType,
): (...args: Params) => Result  => {
  let keyFn: (...arg: Params) => KeyType;
  const resStorage: Result[] = [];
  const keyStorage: KeyType[] = [];
  if (!rawKeyFn) {
    keyFn = (...args) => args[0]
  } else {
    keyFn = rawKeyFn;
  }
  return (...fnArgs) => {
    const key = keyFn(...fnArgs);
    const keyIndex = keyStorage.indexOf(key);
    if (keyIndex !== -1) {
      return resStorage[keyIndex];
    }
    const fnRes: Result = fn(...fnArgs);
    resStorage.push(fnRes);
    keyStorage.push(key);
    return fnRes;
  };
};
