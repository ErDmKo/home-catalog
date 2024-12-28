import { cont } from './cont';
import { bindArg } from './bind';

export const noop = () => {};

export const maybe =
    (resolve: Function, reject: Function = noop) =>
    (fn: Function) => {
        try {
            return fn(resolve, reject);
        } catch (e) {
            return reject(e);
        }
    };
export const maybeOf =
    (fn: Function) =>
    (...args: any[]) =>
        bindArg((resolve: Function) => resolve(fn(...args)), cont);
